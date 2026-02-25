import type { Summary } from '../types';
import { IconSpark } from './Icons';

type Props = { summary: Summary };

export default function AISummary({ summary }: Props) {
  if (!summary || typeof summary !== 'object') return null;
  const total = summary.total_found;
  const returned = summary.returned;
  const explanation = summary.ai_explanation;
  return (
    <>
      {total !== undefined && typeof total === 'number' && (
        <p className="resultMeta">
          Found {total} restaurant(s), showing {typeof returned === 'number' ? returned : total}.
        </p>
      )}
      {explanation && typeof explanation === 'string' && (
        <div className="summaryBox">
          <strong className="summaryBoxTitle">
            <IconSpark size={16} className="summaryBoxIcon" /> AI Summary
          </strong>
          <p className="summaryBoxText">{explanation}</p>
        </div>
      )}
    </>
  );
}
