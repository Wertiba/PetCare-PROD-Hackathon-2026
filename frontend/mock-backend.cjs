// Test-only mock that mimics FastAPI-Fish auth endpoints on :8080.
// Same routes, payloads, cookie behavior, CORS, and error shapes as the backend.
const http = require('node:http');

const users = new Map(); // email -> {user, password}
const refreshCookies = new Map(); // token -> email
let counter = 0;
let posts = []; // загружаются с jsonplaceholder при старте
let postCounter = 0;

const CORS = {
  'Access-Control-Allow-Origin': 'http://localhost:3000',
  'Access-Control-Allow-Credentials': 'true',
  'Access-Control-Allow-Methods': '*',
  'Access-Control-Allow-Headers': '*',
};

function uuid() {
  counter += 1;
  return `00000000-0000-4000-8000-${String(counter).padStart(12, '0')}`;
}

function userDto(u) {
  return {
    id: u.id,
    email: u.email,
    fullName: u.fullName,
    role: u.role,
    isActive: true,
    createdAt: '2026-01-01T00:00:00Z',
    updatedAt: '2026-01-01T00:00:00Z',
    createdBy: u.id,
  };
}

function parseCookies(header) {
  const out = {};
  (header || '').split(';').forEach((p) => {
    const i = p.indexOf('=');
    if (i > -1)
      out[p.slice(0, i).trim()] = decodeURIComponent(
        p.slice(i + 1).trim(),
      );
  });
  return out;
}

function send(res, status, body, extra = {}) {
  const payload =
    body === undefined ? '' : JSON.stringify(body);
  res.writeHead(status, {
    ...CORS,
    'Content-Type': 'application/json',
    ...extra,
  });
  res.end(payload);
}

function setRefresh(res, token) {
  return {
    'Set-Cookie': `refreshToken=${token}; Path=/; HttpOnly; SameSite=Lax; Max-Age=2592000`,
  };
}

function errorBody(code, message) {
  return {
    code,
    message,
    traceId: uuid(),
    timestamp: '2026-01-01T00:00:00Z',
    path: '/api/v1/x',
  };
}

const server = http.createServer((req, res) => {
  let data = '';
  req.on('data', (c) => (data += c));
  req.on('end', () => {
    const body = data ? JSON.parse(data) : {};
    const cookies = parseCookies(req.headers.cookie);
    const path = req.url.split('?')[0];
    const auth = req.headers.authorization || '';
    const bearerUser = auth.startsWith('Bearer ')
      ? [...users.values()].find(
          (u) => u.accessToken === auth.slice(7),
        )
      : null;

    console.log(
      req.method,
      path,
      '->',
      req.statusCode || '',
    );

    if (req.method === 'OPTIONS') {
      res.writeHead(204, CORS);
      return res.end();
    }

    if (
      path === '/api/v1/auth/register' &&
      req.method === 'POST'
    ) {
      const { email, password, fullName } = body;
      const fieldErrors = [];
      if (typeof email !== 'string' || !email.includes('@'))
        fieldErrors.push({
          field: 'email',
          issue: 'value is not a valid email address',
          rejectedValue: email,
        });
      if (
        typeof password !== 'string' ||
        password.length < 8
      )
        fieldErrors.push({
          field: 'password',
          issue:
            'Password must be between 8 and 72 characters',
          rejectedValue: undefined,
        });
      if (
        typeof fullName !== 'string' ||
        !/^[а-яА-Яa-zA-Z0-9 _-]{2,200}$/.test(fullName)
      )
        fieldErrors.push({
          field: 'fullName',
          issue: 'String should match pattern',
          rejectedValue: fullName,
        });
      if (fieldErrors.length)
        return send(res, 422, {
          code: 'VALIDATION_FAILED',
          message: 'Some fields are not correct.',
          traceId: uuid(),
          timestamp: '2026-01-01T00:00:00Z',
          path,
          fieldErrors,
        });
      if (users.has(email))
        return send(
          res,
          409,
          errorBody(
            'EMAIL_ALREADY_EXISTS',
            'User with this email already exists',
          ),
        );
      const u = {
        id: uuid(),
        email,
        fullName,
        role: 'USER',
        password,
      };
      u.accessToken = `access-${u.id}`;
      users.set(email, u);
      const refresh = `refresh-${u.id}`;
      refreshCookies.set(refresh, email);
      return send(
        res,
        201,
        {
          accessToken: u.accessToken,
          expiresIn: 900,
          user: userDto(u),
        },
        setRefresh(res, refresh),
      );
    }

    if (
      path === '/api/v1/auth/login' &&
      req.method === 'POST'
    ) {
      const u = users.get(body.email);
      if (!u || u.password !== body.password)
        return send(
          res,
          401,
          errorBody(
            'UNAUTHORIZED',
            'Invalid email or password',
          ),
        );
      u.accessToken = `access-${u.id}-${Date.now()}`;
      const refresh = `refresh-${u.id}-${Date.now()}`;
      refreshCookies.set(refresh, u.email);
      return send(
        res,
        200,
        {
          accessToken: u.accessToken,
          expiresIn: 900,
          user: userDto(u),
        },
        setRefresh(res, refresh),
      );
    }

    if (
      path === '/api/v1/auth/refresh' &&
      req.method === 'POST'
    ) {
      const email = refreshCookies.get(
        cookies.refreshToken,
      );
      if (!email)
        return send(
          res,
          401,
          errorBody(
            'UNAUTHORIZED',
            'The token is missing or invalid',
          ),
        );
      const u = users.get(email);
      u.accessToken = `access-${u.id}-${Date.now()}`;
      const refresh = `refresh-${u.id}-${Date.now()}`;
      refreshCookies.delete(cookies.refreshToken);
      refreshCookies.set(refresh, email);
      return send(
        res,
        200,
        { accessToken: u.accessToken, expiresIn: 900 },
        setRefresh(res, refresh),
      );
    }

    if (
      path === '/api/v1/auth/logout' &&
      req.method === 'POST'
    ) {
      if (
        !cookies.refreshToken ||
        !refreshCookies.has(cookies.refreshToken)
      )
        return send(
          res,
          401,
          errorBody(
            'UNAUTHORIZED',
            'The token is missing or invalid',
          ),
        );
      refreshCookies.delete(cookies.refreshToken);
      return send(res, 204, undefined, {
        'Set-Cookie':
          'refreshToken=; Path=/; HttpOnly; SameSite=Lax; Max-Age=0',
      });
    }

    if (
      path === '/api/v1/users/me' &&
      req.method === 'GET'
    ) {
      if (!bearerUser)
        return send(
          res,
          401,
          errorBody(
            'UNAUTHORIZED',
            'The token is missing or invalid',
          ),
        );
      return send(res, 200, userDto(bearerUser));
    }

    const postMatch = path.match(
      /^\/api\/v1\/posts(?:\/(\d+))?$/,
    );
    if (postMatch) {
      const id = postMatch[1] ? Number(postMatch[1]) : null;
      const post = posts.find((p) => p.id === id);

      // GET публичный, остальные методы только с токеном
      if (req.method !== 'GET' && !bearerUser)
        return send(
          res,
          401,
          errorBody(
            'UNAUTHORIZED',
            'The token is missing or invalid',
          ),
        );

      if (req.method === 'GET' && id === null)
        return send(res, 200, posts);

      if (req.method === 'POST' && id === null) {
        const { title, body: text } = body;
        if (typeof title !== 'string' || typeof text !== 'string')
          return send(
            res,
            422,
            errorBody(
              'VALIDATION_FAILED',
              'title and body are required',
            ),
          );
        postCounter += 1;
        const created = {
          id: postCounter,
          userId: bearerUser.id,
          title,
          body: text,
        };
        posts.push(created);
        return send(res, 201, created);
      }

      if (id !== null) {
        if (!post)
          return send(
            res,
            404,
            errorBody('NOT_FOUND', 'Post not found'),
          );
        if (req.method === 'GET') return send(res, 200, post);
        if (req.method === 'PATCH') {
          if (typeof body.title === 'string')
            post.title = body.title;
          if (typeof body.body === 'string')
            post.body = body.body;
          return send(res, 200, post);
        }
        if (req.method === 'DELETE') {
          posts = posts.filter((p) => p.id !== id);
          return send(res, 204, undefined);
        }
      }
    }

    send(
      res,
      404,
      errorBody('NOT_FOUND', 'Resource not found'),
    );
  });
});

fetch('https://jsonplaceholder.typicode.com/posts')
  .then((r) => r.json())
  .then((data) => {
    posts = data;
    postCounter = Math.max(0, ...data.map((p) => p.id));
    console.log(`loaded ${posts.length} posts`);
  })
  .catch((e) => console.log('failed to load posts', e.message));

server.listen(8080, () =>
  console.log('mock backend on :8080'),
);
