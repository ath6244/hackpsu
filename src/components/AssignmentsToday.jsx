import React, { useEffect, useState } from 'react';

const API_BASE = 'http://localhost:5001'; // backend running on port 5001

const AssignmentsToday = ({ date }) => {
  const [assignments, setAssignments] = useState([]);
  const [loading, setLoading] = useState(true);
  const [error, setError] = useState(null);

  useEffect(() => {
    const fetchAssignments = async () => {
      setLoading(true);
      setError(null);
      try {
        const url = `${API_BASE}/api/assignments/today?date=${date}`;
        const res = await fetch(url);
        if (!res.ok) throw new Error(`HTTP ${res.status}`);
        const data = await res.json();
        // annotate assignments with local completed flag
        const annotated = data.assignments.map(a => ({ ...a, completed: false }));
        setAssignments(annotated);
      } catch (err) {
        console.error('Failed to fetch assignments', err);
        setError('Failed to load assignments');
      } finally {
        setLoading(false);
      }
    };

    if (date) fetchAssignments();
  }, [date]);

  const markComplete = async (course_id, assignment_id, idx) => {
    try {
      const res = await fetch(`${API_BASE}/api/assignments/${course_id}/${assignment_id}/complete`, {
        method: 'POST',
        headers: { 'Content-Type': 'application/json' }
      });
      const payload = await res.json();
      if (!res.ok) throw new Error(payload.detail || payload.error || 'Failed');

      // optimistic update
      setAssignments(prev => {
        const copy = [...prev];
        copy[idx] = { ...copy[idx], completed: true };
        return copy;
      });
    } catch (err) {
      console.error('Error marking complete', err);
      alert('Could not mark assignment complete. Check console for details.');
    }
  };

  if (loading) return <div className="text-gray-300">Loading assignments...</div>;
  if (error) return <div className="text-red-400">{error}</div>;
  if (!assignments || assignments.length === 0) return <div className="text-gray-400">No assignments due for this date.</div>;

  return (
    <div className="mt-8">
      <h2 className="text-2xl font-semibold text-white mb-4">Assignments Due {date}</h2>
      <div className="space-y-3">
        {assignments.map((a, idx) => (
          <div key={`${a.course_id}-${a.assignment_id}`} className="p-4 rounded-md bg-gray-800 border border-gray-700 flex items-center justify-between">
            <div>
              <div className="text-white font-medium">{a.name}</div>
              <div className="text-sm text-gray-400">{a.course_name} — Due: {a.due_at ? new Date(a.due_at).toLocaleString() : 'N/A'}</div>
            </div>
            <div className="flex items-center space-x-3">
              <label className="inline-flex items-center">
                <input type="checkbox" checked={a.completed} onChange={() => markComplete(a.course_id, a.assignment_id, idx)} className="form-checkbox h-5 w-5 text-green-500" />
                <span className="ml-2 text-sm text-gray-200">Completed</span>
              </label>
              {a.html_url && (
                <a href={a.html_url} target="_blank" rel="noreferrer" className="text-sm text-blue-300 underline">Open</a>
              )}
            </div>
          </div>
        ))}
      </div>
    </div>
  );
};

export default AssignmentsToday;
