import { CreateEventForm } from '@src/features/event/create-event';
import { Suspense } from 'react';

const CreateEventPage = () => {
  return (
    <div>
      <Suspense>
        <CreateEventForm />
      </Suspense>
    </div>
  );
};

export default CreateEventPage;
