import { notFound } from "next/navigation";
import { TopicPage } from "@/components/TopicPage";
import { getTopic } from "@/lib/api";

export async function generateMetadata({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const topic = await getTopic(slug);
  if (!topic) return { title: "Topic Analytics | UPDATES" };
  return {
    title: `${topic.title} | UPDATES Intelligence`,
    description: topic.insight || topic.subtitle,
  };
}

export default async function Page({ params }: { params: Promise<{ slug: string }> }) {
  const { slug } = await params;
  const topic = await getTopic(slug);
  if (!topic) notFound();
  return <TopicPage topic={topic} />;
}
