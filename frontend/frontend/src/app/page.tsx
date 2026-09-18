import Link from 'next/link';

export default function Landing() {
  return (
    <div className="text-center py-20">
      <h1 className="text-4xl font-bold mb-6">Legal RAG Platform</h1>
      <p className="mb-8 text-lg">Get structured legal analysis instantly.</p>
      <Link href="/input" className="bg-accent text-white px-6 py-3 rounded-lg text-lg">Start a case</Link>
    </div>
  );
}
