import type { Campaign, Submission } from './types';

export const demoCampaigns: Campaign[] = [
  {
    id: '11111111-1111-4111-8111-111111111111', title: 'Primeros pasos sin fricción',
    description: 'Revisa el recorrido inicial de SeekerLab y explica qué cambiarías.',
    instructions: ['Explora las campañas disponibles', 'Abre una campaña y revisa las instrucciones', 'Describe un punto de confusión y cómo lo mejorarías'],
    reward_amount: '3.00', currency: 'USDC', estimated_minutes: 5, capacity: 20,
    submitted_count: 0, status: 'open', created_at: '2026-09-10T00:00:00Z',
  },
  {
    id: '22222222-2222-4222-8222-222222222222', title: '¿Se entiende la recompensa?',
    description: 'Comprueba si los importes y las condiciones de una prueba están claros.',
    instructions: ['Localiza la recompensa anunciada', 'Revisa cuándo se cobraría y qué está pendiente', 'Propón una mejora concreta para mostrar esta información'],
    reward_amount: '5.00', currency: 'USDC', estimated_minutes: 8, capacity: 12,
    submitted_count: 0, status: 'open', created_at: '2026-09-10T00:00:00Z',
  },
  {
    id: '33333333-3333-4333-8333-333333333333', title: 'Lectura y accesibilidad',
    description: 'Evalúa el tamaño del texto, los botones y la claridad del formulario.',
    instructions: ['Aumenta el tamaño de fuente en Android', 'Abre el formulario de una campaña', 'Explica qué elementos resultan difíciles de leer o pulsar'],
    reward_amount: '4.00', currency: 'USDC', estimated_minutes: 6, capacity: 15,
    submitted_count: 0, status: 'open', created_at: '2026-09-10T00:00:00Z',
  },
];

// Explicit demonstration mode only. All state resets on a full app reload.
const submissions: Submission[] = [];

export const demoApi = {
  async campaigns(): Promise<Campaign[]> {return demoCampaigns.map(item => ({...item}));},
  async submissions(): Promise<Submission[]> {return [...submissions];},
  async submit(campaignId: string, feedback: string): Promise<Submission> {
    const campaign = demoCampaigns.find(item => item.id === campaignId);
    if (!campaign) throw new Error('Campaña no encontrada');
    if (submissions.some(item => item.campaign_id === campaignId)) throw new Error('Ya has enviado esta prueba');
    if (campaign.status !== 'open' || campaign.submitted_count >= campaign.capacity) throw new Error('No quedan plazas');
    const cleaned = feedback.trim();
    if (cleaned.length < 20 || cleaned.length > 5000) throw new Error('Escribe entre 20 y 5000 caracteres');
    const submission: Submission = {
      id: `demo-${Date.now()}`, campaign_id: campaignId, feedback: cleaned,
      status: 'pending_review', created_at: new Date().toISOString(),
    };
    submissions.unshift(submission);
    campaign.submitted_count += 1;
    return submission;
  },
};
