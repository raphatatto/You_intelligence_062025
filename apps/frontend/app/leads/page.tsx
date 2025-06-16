import LeadsTable from '@/components/leads/LeadsTable';
import {leadsMock } from '@/app/data/leads';      // ← array mock

export const metadata = { title: 'Leads • You.On' };

export default function LeadsPage() {
  return (
    <section className="space-y-6">
      <h1 className="text-2xl font-bold">Leads ({leadsMock.length})</h1>
      <LeadsTable rows={leadsMock} />
    </section>
  );
}
