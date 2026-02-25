type Props = { message: string };

export default function ApiHint({ message }: Props) {
  return (
    <div className="apiHint">
      <strong>API not reachable.</strong> Start the backend first: from project root run{' '}
      <code>./start-api.sh</code> or <code>PYTHONPATH=. python phase2/api/main.py</code>. Then
      refresh this page. Error: {message}
    </div>
  );
}
