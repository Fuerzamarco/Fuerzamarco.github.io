export interface FaqItem {
  question: string;
  answer: string;
}

const FAQ_HEADINGS = [
  'preguntas frecuentes',
  'faqs',
  'faq',
  'preguntas y respuestas',
  'q&a',
];

function normalizeHeading(text: string): string {
  // Strip "H2 — " or "H3 - " prefix the prompt may emit literally.
  return text
    .toLowerCase()
    .replace(/^[h][1-6]\s*[—–-]\s*/i, '')
    .replace(/^[—–-]\s*/, '')
    .trim();
}

function isFaqHeading(text: string): boolean {
  const normalized = normalizeHeading(text);
  return FAQ_HEADINGS.some(
    (h) => normalized === h || normalized.startsWith(h + ' ')
  );
}

/**
 * Extracts Q/A pairs from a markdown body's FAQ section.
 *
 * Recognises headings like "## Preguntas frecuentes", "## FAQs",
 * "## H2 — Preguntas frecuentes", etc. Stops at the next `## ` heading.
 *
 * Each Q is detected by a line starting with `**...**` (bold-only line).
 * The A is everything below until the next Q or section end.
 */
export function parseFaqs(body: string): FaqItem[] {
  const lines = body.split('\n');
  let inFaq = false;
  let faqStart = -1;
  let faqEnd = lines.length;

  for (let i = 0; i < lines.length; i++) {
    const h2Match = lines[i].match(/^##\s+(.+?)\s*$/);
    if (!h2Match) continue;
    if (!inFaq) {
      if (isFaqHeading(h2Match[1])) {
        inFaq = true;
        faqStart = i + 1;
      }
    } else {
      faqEnd = i;
      break;
    }
  }

  if (faqStart === -1) return [];

  const items: FaqItem[] = [];
  let currentQ: string | null = null;
  let currentA: string[] = [];

  const flush = () => {
    if (currentQ) {
      const answer = currentA.join('\n').trim();
      if (answer) items.push({ question: currentQ, answer });
      currentQ = null;
      currentA = [];
    }
  };

  for (let i = faqStart; i < faqEnd; i++) {
    const line = lines[i];
    const qMatch = line.trim().match(/^\*\*(.+?)\*\*\s*$/);
    if (qMatch) {
      flush();
      currentQ = qMatch[1].trim();
    } else if (currentQ !== null) {
      currentA.push(line);
    }
  }
  flush();

  return items;
}

/**
 * Strips common markdown for use inside JSON-LD `text` fields.
 * Plain-text output, single-line, no formatting.
 */
export function stripMarkdown(s: string): string {
  return s
    .replace(/\*\*(.+?)\*\*/g, '$1')
    .replace(/\*(.+?)\*/g, '$1')
    .replace(/\[([^\]]+)\]\([^)]+\)/g, '$1')
    .replace(/`([^`]+)`/g, '$1')
    .replace(/\n\n+/g, ' ')
    .replace(/\n/g, ' ')
    .replace(/\s+/g, ' ')
    .trim();
}
