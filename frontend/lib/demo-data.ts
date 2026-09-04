import type { Story, Topic } from "@/types";
export const stories:Story[] = [
  {id:"p1",topic_slug:"maratha-reservation-protest-2026",title:"Maratha Reservation Protest: Manoj Jarange Continues Fast, Sets September 11 Deadline",category:"Protest",time:"2m ago",image:"/images/real-city-protest.jpg",live:true,summary:"Manoj Jarange continued his reservation agitation in Jalna after seeking action on Maratha quota and Kunbi certificate demands."},
  {id:"p2",topic_slug:"tukaram-mundhe-fda-testing-surge",title:"Maharashtra FDA Testing Rises 300% Under IAS Officer Tukaram Mundhe",category:"India",time:"5m ago",image:"/images/real-data-check.jpg",live:true,summary:"Maharashtra FDA reported a sharp increase in statewide sample collection and testing after Tukaram Mundhe took charge as commissioner."},
  {id:"1",topic_slug:"reservation-protest",title:"CJP Protest Intensifies Across Multiple States",category:"India",time:"2h ago",image:"/images/real-protest.jpg",live:true},
 {id:"2",topic_slug:"student-community-food-drives",title:"Students Unite for Community Food Drives",category:"India",time:"4h ago",image:"/images/real-food-drive.jpg"},
 {id:"3",topic_slug:"supreme-court-reservation-hearing",title:"Supreme Court Hearing on Reservation Policy",category:"Laws",time:"5h ago",image:"/images/real-supreme-court.jpg"},
 {id:"4",topic_slug:"university-campus-protests",title:"University Campus Protests: Demands & Updates",category:"Education",time:"3h ago",image:"/images/real-campus.jpg"},
 {id:"5",topic_slug:"reservation-debate-un-forum",title:"India Raises Reservation Debate at UN Forum",category:"Foreign Affairs",time:"6h ago",image:"/images/real-un-forum.jpg"},
 {id:"6",topic_slug:"city-wide-protests",title:"City-Wide Protests Disrupt Normal Life",category:"India",time:"1h ago",image:"/images/real-city-protest.jpg"},
 {id:"7",topic_slug:"nationwide-bharat-bandh",title:"Dalit Organisations Call for Nationwide Bharat Bandh",category:"Protest",time:"6h ago",image:"/images/real-bharat-bandh.png"},
 {id:"8",topic_slug:"reservation-framework-bill",title:"New Bill Proposes Changes to Reservation Framework",category:"Laws",time:"8h ago",image:"/images/real-bill.jpg"},
 {id:"9",topic_slug:"aspirants-reservation-debate",title:"Aspirants Speak: The Other Side of the Debate",category:"Opinions",time:"7h ago",image:"/images/real-aspirants.jpg"},
 {id:"10",topic_slug:"reservation-rural-india",title:"How Reservation Impacts Rural India",category:"India",time:"9h ago",image:"/images/real-rural.jpg"},
 {id:"11",topic_slug:"reservation-fact-check",title:"Data Check: Facts vs Claims on Reservations",category:"Analysis",time:"10h ago",image:"/images/real-data-check.jpg"},
 {id:"12",topic_slug:"ground-zero-reservation-voices",title:"Voices from Ground Zero: Stories You Didn't Hear",category:"India",time:"12h ago",image:"/images/real-ground-zero.jpg"},
];
export const reservationTopic:Topic={slug:"reservation-protest",title:"Latest Reservation Protest",subtitle:"Public sentiment & conversation analysis",totalConversations:52480,updated:"2 min ago",sentiment:{negative:55,neutral:27,positive:18},sentimentChange:8,insight:"Public conversation is currently leaning negative. Major concerns revolve around fairness, implementation and access to opportunities, while supportive conversations focus on representation and social equity.",audience:{geography:"Delhi NCR",language:"Hindi / Hinglish",age:"18–24 years",ageConfidence:"Medium",interests:"Students & job aspirants",topics:["Reservation","Jobs","Education","Equality"],platform:"X leads the discussion"},drivers:[{title:"Fairness & Equality",description:"Most people are debating fairness, equality and equal opportunities for all.",status:"Top concern"},{title:"Education & Admissions",description:"Large volume of discussion on college admissions, seat allocation and cutoff impact.",status:"Rising"},{title:"Employment Opportunities",description:"Debates around job reservation, private-sector inclusion and economic impact.",status:"Rising"},{title:"Government Policy",description:"Opinions on policy implementation, revisions and the legal framework.",status:"Stable"}],voices:[{quote:"Reservation is important for representation and giving equal opportunities to everyone.",label:"Supporting voice",tone:"supporting"},{quote:"Merit is being compromised. There should be a balance between both.",label:"Concerned voice",tone:"concerned"},{quote:"What about economic background? Shouldn’t that matter more than caste?",label:"Neutral / questioning",tone:"neutral"}],trends:[{time:"06:00",volume:6200,sentiment:47},{time:"09:00",volume:7100,sentiment:48},{time:"12:00",volume:8400,sentiment:50},{time:"15:00",volume:10600,sentiment:51},{time:"18:00",volume:13100,sentiment:54},{time:"Now",volume:15480,sentiment:55}],confidence:{sources:["X","YouTube","Telegram","Reddit"],qualified:28410,lowSignal:6281,level:"High"},network:{nodes:[{id:"students",label:"Student communities",group:"origin",size:36},{id:"education",label:"Education forums",group:"amplifier",size:28},{id:"policy",label:"Policy discussions",group:"amplifier",size:32},{id:"public",label:"General public",group:"audience",size:42},{id:"jobs",label:"Job aspirants",group:"audience",size:26}],edges:[{source:"students",target:"education",weight:8},{source:"students",target:"policy",weight:6},{source:"education",target:"public",weight:7},{source:"policy",target:"public",weight:9},{source:"jobs",target:"policy",weight:5}]}};

export const marathaTopic: Topic = {
  slug: "maratha-reservation-protest-2026",
  title: "Maratha Reservation Protest 2026",
  subtitle: "Public sentiment & conversation analysis",
  category: "Protest",
  image: "/images/real-protest.jpg",
  totalConversations: 10,
  updated: "Recent public signals",
  sentiment: { negative: 20, neutral: 70, positive: 10 },
  sentimentChange: 0,
  insight: "Public discussion around the Maratha reservation centers on legal validation of Kunbi certificates, equitable quota distribution, and civic mobilization across Maharashtra.",
  audience: {
    geography: "Maharashtra",
    geographyConfidence: "High",
    language: "Marathi / Hindi / English",
    languageConfidence: "High",
    age: "18–35 years",
    ageConfidence: "Medium",
    interests: "Social equity & student admissions",
    topics: ["Kunbi Certificate", "SEBC Quota", "Jarange Patil", "Civic Rights"],
    platform: "Reddit & Public Forums"
  },
  drivers: [
    { title: "Kunbi Certificate & OBC Inclusion", description: "Discussions surrounding eligibility criteria and legal classification.", status: "Top concern" },
    { title: "Constitutional & Court Validity", description: "Anticipation of judicial review and statutory requirements.", status: "Rising" },
    { title: "Civic & Electoral Influence", description: "Discussions surrounding local elections and policy decisions.", status: "Stable" }
  ],
  voices: [
    { quote: "Could anyone explain the impact and what a Kunbi certificate means for students?", label: "Neutral / questioning", tone: "neutral" },
    { quote: "Jarange knows the proposal may face another constitutional challenge.", label: "Concerned voice", tone: "concerned" },
    { quote: "Let's end caste-based reservations and keep support based on disability and financial status.", label: "Supporting reform", tone: "supporting" }
  ],
  trends: [
    { time: "06:00", volume: 320, sentiment: 25 },
    { time: "12:00", volume: 680, sentiment: 22 },
    { time: "Now", volume: 950, sentiment: 20 }
  ],
  confidence: {
    sources: ["Reddit", "Public Forums"],
    qualified: 10,
    lowSignal: 0,
    level: "Medium"
  },
  network: {
    nodes: [
      { id: "community", label: "Maharashtra communities", group: "origin", size: 36 },
      { id: "legal", label: "Legal observers", group: "amplifier", size: 30 },
      { id: "students", label: "Student aspirants", group: "audience", size: 34 }
    ],
    edges: [
      { source: "community", target: "legal", weight: 6 },
      { source: "community", target: "students", weight: 8 }
    ]
  }
};

export const tukaramTopic: Topic = {
  slug: "tukaram-mundhe-fda-testing-surge",
  title: "Tukaram Mundhe Leads State-Wide FDA Testing Surge",
  subtitle: "Public sentiment & conversation analysis",
  category: "Health & Safety",
  image: "/images/real-data-check.jpg",
  totalConversations: 10,
  updated: "Recent public signals",
  sentiment: { negative: 10, neutral: 70, positive: 20 },
  sentimentChange: 5,
  insight: "Public response to the FDA testing surge under IAS officer Tukaram Mundhe is largely supportive, highlighting consumer safety, transparent labeling, and rigorous market enforcement.",
  audience: {
    geography: "Maharashtra / Mumbai / Pune",
    geographyConfidence: "High",
    language: "English / Marathi",
    languageConfidence: "High",
    age: "21–45 years",
    ageConfidence: "Medium",
    interests: "Public health, food safety & good governance",
    topics: ["Food Adulteration", "FDA Inspection", "Consumer Protection", "IAS Enforcement"],
    platform: "Reddit & News Discussion"
  },
  drivers: [
    { title: "Food Safety & Consumer Protection", description: "Intensified raids against adulteration and illicit networks.", status: "Top concern" },
    { title: "Administrative Accountability", description: "Strong public appreciation for fearless bureaucratic enforcement.", status: "Rising" },
    { title: "Due Process & Compliance", description: "Calls for proportionate regulations and transparent inspection protocols.", status: "Stable" }
  ],
  voices: [
    { quote: "Thank you, Tukaram Mundhe. Officers like you make me feel there is still hope.", label: "Supporting voice", tone: "supporting" },
    { quote: "FDA enforcement should be strict, consistent and follow due process.", label: "Concerned voice", tone: "concerned" },
    { quote: "Watching the gap between food-safety rules and enforcement close is meaningful.", label: "Neutral / observer", tone: "neutral" }
  ],
  trends: [
    { time: "06:00", volume: 210, sentiment: 12 },
    { time: "12:00", volume: 540, sentiment: 11 },
    { time: "Now", volume: 890, sentiment: 10 }
  ],
  confidence: {
    sources: ["Reddit", "Public Disclosures"],
    qualified: 10,
    lowSignal: 0,
    level: "Medium"
  },
  network: {
    nodes: [
      { id: "consumers", label: "Consumers & Citizens", group: "origin", size: 38 },
      { id: "governance", label: "Administrative Watch", group: "amplifier", size: 32 },
      { id: "retailers", label: "Retail & Manufacturing", group: "audience", size: 28 }
    ],
    edges: [
      { source: "consumers", target: "governance", weight: 7 },
      { source: "governance", target: "retailers", weight: 5 }
    ]
  }
};

export const fallbackTopicsMap: Record<string, Topic> = {
  [reservationTopic.slug]: reservationTopic,
  [marathaTopic.slug]: marathaTopic,
  [tukaramTopic.slug]: tukaramTopic,
};

export function buildPreviewTopic(slug: string): Topic {
  const story = stories.find(item => item.topic_slug === slug);
  const title = story?.title ?? slug.replace(/-/g, " ").replace(/\b\w/g, l => l.toUpperCase());
  return {
    slug,
    title,
    subtitle: "Public sentiment & conversation analysis",
    image: story?.image ?? "/images/real-data-check.jpg",
    category: story?.category ?? "Analysis",
    preview: true,
    totalConversations: 0,
    updated: "Awaiting collected comments",
    sentiment: { negative: 32, neutral: 48, positive: 20 },
    sentimentChange: 0,
    insight: `Initial topic preview for “${title}”. Live public conversations and comment analytics will appear as soon as the background intelligence worker finishes ingestion.`,
    audience: {
      geography: "National",
      geographyConfidence: "Medium",
      language: "Hindi / English",
      languageConfidence: "Medium",
      age: "18–35 years",
      ageConfidence: "Unavailable",
      interests: "Public affairs & policy debate",
      topics: [title.split(" ")[0], "Public opinion", "Policy"],
      platform: "Multi-platform"
    },
    drivers: [
      { title: "Public Attention", description: `Growing focus and social activity around “${title}”.`, status: "Top concern" },
      { title: "Developing Narrative", description: "Emerging conversation themes from verified news and indexed sources.", status: "Rising" }
    ],
    voices: [],
    trends: [
      { time: "06:00", volume: 140, sentiment: 30 },
      { time: "12:00", volume: 290, sentiment: 31 },
      { time: "Now", volume: 420, sentiment: 32 }
    ],
    confidence: {
      sources: ["Story metadata", "Public web signals"],
      qualified: 420,
      lowSignal: 15,
      level: "Medium"
    },
    network: {
      nodes: [
        { id: "community", label: "Public communities", group: "origin", size: 30 },
        { id: "media", label: "News & Media", group: "amplifier", size: 25 }
      ],
      edges: [
        { source: "community", target: "media", weight: 4 }
      ]
    }
  };
}
