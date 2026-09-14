// Matches the initial FastAPI schemas. Decimal values travel as strings.
export type Currency = 'USDC' | 'SKR';

export interface Campaign {
  id: string;
  title: string;
  description: string;
  instructions: string[];
  reward_amount: string;
  currency: Currency;
  estimated_minutes: number;
  capacity: number;
  submitted_count: number;
  status: 'open' | 'closed';
  created_at: string;
}

export interface Submission {
  id: string;
  campaign_id: string;
  feedback: string;
  status: string;
  created_at: string;
}
