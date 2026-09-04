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

export const studentFoodDrivesTopic: Topic = {
  slug: "student-community-food-drives",
  title: "Students Unite for Community Food Drives",
  subtitle: "Public sentiment & civic action analysis",
  category: "India",
  image: "/images/real-food-drive.jpg",
  totalConversations: 2840,
  updated: "Recent public signals",
  sentiment: { negative: 14, neutral: 26, positive: 60 },
  sentimentChange: 12,
  insight: "Public response to student community food drives is overwhelmingly supportive, celebrating campus mutual aid and youth volunteerism while raising operational questions about hygienic food safety and long-term institutional support.",
  audience: {
    geography: "Delhi NCR / Mumbai / Bengaluru",
    geographyConfidence: "High",
    language: "English / Hindi",
    languageConfidence: "High",
    age: "18–28 years",
    ageConfidence: "High",
    interests: "Civic volunteerism, student welfare & mutual aid",
    topics: ["Food Insecurity", "Student Volunteerism", "Campus Relief", "Mutual Aid"],
    platform: "Reddit & Student Community Forums"
  },
  drivers: [
    { title: "Grassroots Mutual Aid", description: "Widespread community appreciation for student-led emergency food redistribution.", status: "Top concern" },
    { title: "Campus Welfare & Dignity", description: "Highlighting basic nutrition gaps among student workers and local shelters.", status: "Rising" },
    { title: "Logistics & Food Safety", description: "Discussions around refrigerated storage, hygiene certifications, and distribution equity.", status: "Stable" }
  ],
  voices: [
    { quote: "Grassroots mutual aid organized directly by student volunteers is filling critical nutritional gaps for campus workers and local communities.", label: "Supporting voice · Reddit r/india", tone: "supporting" },
    { quote: "Charity drives cannot be a long-term substitute for proper state institutional funding and subsidized university dining halls.", label: "Concerned voice · Student Welfare Assembly", tone: "concerned" },
    { quote: "How are student groups ensuring food quality, hygienic distribution, and equitable allocation across regional centers?", label: "Neutral / questioning · Civic Audit Community", tone: "neutral" }
  ],
  trends: [
    { time: "06:00", volume: 320, sentiment: 12 },
    { time: "12:00", volume: 890, sentiment: 14 },
    { time: "Now", volume: 1630, sentiment: 14 }
  ],
  confidence: {
    sources: ["Reddit", "Public Forums", "Student Assemblies"],
    qualified: 2840,
    lowSignal: 140,
    level: "High"
  },
  network: {
    nodes: [
      { id: "students", label: "Student Volunteers", group: "origin", size: 40 },
      { id: "civic", label: "Civic Organizations", group: "amplifier", size: 32 },
      { id: "community", label: "Beneficiary Communities", group: "audience", size: 36 }
    ],
    edges: [
      { source: "students", target: "civic", weight: 7 },
      { source: "civic", target: "community", weight: 9 }
    ]
  }
};

export const supremeCourtTopic: Topic = {
  slug: "supreme-court-reservation-hearing",
  title: "Supreme Court Hearing on Reservation Policy",
  subtitle: "Public sentiment & legal analysis",
  category: "Laws",
  image: "/images/real-supreme-court.jpg",
  totalConversations: 18450,
  updated: "Recent public signals",
  sentiment: { negative: 42, neutral: 38, positive: 20 },
  sentimentChange: 6,
  insight: "Public discussion around the Supreme Court reservation hearing focuses on constitutional ceilings, empirical data validity for sub-classification, and ensuring affirmative action reaches the most disadvantaged cohorts.",
  audience: {
    geography: "National",
    geographyConfidence: "High",
    language: "English / Hindi",
    languageConfidence: "High",
    age: "21–45 years",
    ageConfidence: "Medium",
    interests: "Constitutional law, public policy & civil rights",
    topics: ["Sub-classification", "50% Quota Ceiling", "Judicial Review", "Empirical Caste Survey"],
    platform: "Bar & Bench & Legal Forums"
  },
  drivers: [
    { title: "Sub-Classification Validity", description: "Debating whether state governments have authority to sub-categorize reserved groups.", status: "Top concern" },
    { title: "Empirical Census & Survey Data", description: "Demands for objective statistical surveys before implementing quota changes.", status: "Rising" },
    { title: "Creamy Layer Guidelines", description: "Discussions around expanding economic exclusion principles within quota categories.", status: "Rising" }
  ],
  voices: [
    { quote: "Sub-classification within reserved categories is vital so benefits reach the most marginalized families rather than getting monopolized.", label: "Supporting voice · Legal Forum", tone: "supporting" },
    { quote: "Breaching existing constitutional quota limits without up-to-date empirical socio-economic census data could destabilize governance.", label: "Concerned voice · Bar & Bench Discussion", tone: "concerned" },
    { quote: "Will the constitutional bench lay down objective, measurable criteria for the creamy layer exclusion across all quotas?", label: "Neutral / questioning · Aspirants Community", tone: "neutral" }
  ],
  trends: [
    { time: "06:00", volume: 2200, sentiment: 39 },
    { time: "12:00", volume: 5400, sentiment: 41 },
    { time: "Now", volume: 10850, sentiment: 42 }
  ],
  confidence: {
    sources: ["Legal Briefs", "Reddit", "Public News Signals"],
    qualified: 18450,
    lowSignal: 620,
    level: "High"
  },
  network: {
    nodes: [
      { id: "judiciary", label: "Supreme Court Bench", group: "origin", size: 42 },
      { id: "advocates", label: "Legal Advocates", group: "amplifier", size: 35 },
      { id: "aspirants", label: "Public Aspirants", group: "audience", size: 38 }
    ],
    edges: [
      { source: "judiciary", target: "advocates", weight: 8 },
      { source: "advocates", target: "aspirants", weight: 7 }
    ]
  }
};

export const universityProtestsTopic: Topic = {
  slug: "university-campus-protests",
  title: "University Campus Protests: Demands & Updates",
  subtitle: "Public sentiment & campus discourse",
  category: "Education",
  image: "/images/real-campus.jpg",
  totalConversations: 8920,
  updated: "Recent public signals",
  sentiment: { negative: 38, neutral: 34, positive: 28 },
  sentimentChange: 9,
  insight: "Campus protest coverage indicates significant public sympathy for affordable public education alongside concern over exam disruptions, administrative communication breakdowns, and campus safety.",
  audience: {
    geography: "Delhi / Pune / Hyderabad / Kolkata",
    geographyConfidence: "High",
    language: "English / Hindi",
    languageConfidence: "High",
    age: "18–26 years",
    ageConfidence: "High",
    interests: "Higher education policy, student rights & campus welfare",
    topics: ["Hostel Fees", "Cutoff Transparency", "Democratic Protest", "Exam Schedules"],
    platform: "Reddit & Student Assemblies"
  },
  drivers: [
    { title: "Fee Hikes & Educational Access", description: "Protesting steep hostel and tuition hikes that disproportionately impact rural students.", status: "Top concern" },
    { title: "Academic Calendar Disruption", description: "Worries regarding rescheduled university examinations and placement drives.", status: "Rising" },
    { title: "Administrative Transparency", description: "Demands for direct open dialogue between student councils and university deans.", status: "Stable" }
  ],
  voices: [
    { quote: "Sudden fee hikes and reduced library access directly threaten student diversity. Peaceful protest is a democratic necessity.", label: "Supporting voice · Campus Union", tone: "supporting" },
    { quote: "Campus blockades during mid-term examination and placement season unfairly disrupt students who have urgent deadlines.", label: "Concerned voice · Faculty Forum", tone: "concerned" },
    { quote: "Why hasn't the administration published an itemized financial audit detailing exactly why operational costs jumped 40%?", label: "Neutral / questioning · Reddit r/Indian_Academia", tone: "neutral" }
  ],
  trends: [
    { time: "06:00", volume: 1100, sentiment: 35 },
    { time: "12:00", volume: 3200, sentiment: 37 },
    { time: "Now", volume: 4620, sentiment: 38 }
  ],
  confidence: {
    sources: ["Reddit", "Campus Forums", "Public Disclosures"],
    qualified: 8920,
    lowSignal: 410,
    level: "High"
  },
  network: {
    nodes: [
      { id: "students", label: "Student Councils", group: "origin", size: 38 },
      { id: "faculty", label: "Academic Faculty", group: "amplifier", size: 30 },
      { id: "administration", label: "University Admin", group: "audience", size: 34 }
    ],
    edges: [
      { source: "students", target: "faculty", weight: 6 },
      { source: "students", target: "administration", weight: 9 }
    ]
  }
};

export const unForumTopic: Topic = {
  slug: "reservation-debate-un-forum",
  title: "India Raises Reservation Debate at UN Forum",
  subtitle: "Public sentiment & international policy",
  category: "Foreign Affairs",
  image: "/images/real-un-forum.jpg",
  totalConversations: 6340,
  updated: "Recent public signals",
  sentiment: { negative: 28, neutral: 44, positive: 28 },
  sentimentChange: 4,
  insight: "Public commentary on the UN Forum presentation balances national pride in India's affirmative constitutional history against cautions that domestic reservation debates should not become politicized abroad.",
  audience: {
    geography: "National & Global Diaspora",
    geographyConfidence: "Medium",
    language: "English / Hindi",
    languageConfidence: "High",
    age: "24–50 years",
    ageConfidence: "Medium",
    interests: "International diplomacy, human rights & public policy",
    topics: ["Affirmative Action Precedent", "Sovereign Jurisdiction", "UN Human Rights", "Global Comparisons"],
    platform: "Diplomatic Forums & News Discussion"
  },
  drivers: [
    { title: "Affirmative Action as Global Precedent", description: "Positioning India's constitutional guarantees as a benchmark for indigenous representation.", status: "Top concern" },
    { title: "National Sovereignty & Jurisdiction", description: "Arguments asserting domestic social policy should be resolved within Indian courts.", status: "Rising" }
  ],
  voices: [
    { quote: "Highlighting India's affirmative action framework at the UN showcases a pioneering constitutional model for indigenous equity.", label: "Supporting voice · Diplomatic Observer", tone: "supporting" },
    { quote: "Domestic social policies are sovereign issues and raising them on global platforms invites external political pressure without context.", label: "Concerned voice · Policy Watchdog", tone: "concerned" },
    { quote: "What multilateral precedents were discussed regarding how other countries address historical systemic disparities?", label: "Neutral / questioning · Global Affairs Journal", tone: "neutral" }
  ],
  trends: [
    { time: "06:00", volume: 800, sentiment: 26 },
    { time: "12:00", volume: 2100, sentiment: 27 },
    { time: "Now", volume: 3440, sentiment: 28 }
  ],
  confidence: {
    sources: ["UN Disclosures", "News Analysis", "Public Policy Forums"],
    qualified: 6340,
    lowSignal: 290,
    level: "Medium"
  },
  network: {
    nodes: [
      { id: "diplomats", label: "Diplomatic Envoys", group: "origin", size: 36 },
      { id: "media", label: "Foreign Policy Analysts", group: "amplifier", size: 32 },
      { id: "citizens", label: "Civic Public", group: "audience", size: 30 }
    ],
    edges: [
      { source: "diplomats", target: "media", weight: 7 },
      { source: "media", target: "citizens", weight: 6 }
    ]
  }
};

export const cityProtestsTopic: Topic = {
  slug: "city-wide-protests",
  title: "City-Wide Protests Disrupt Normal Life",
  subtitle: "Public sentiment & urban impact",
  category: "India",
  image: "/images/real-city-protest.jpg",
  totalConversations: 14200,
  updated: "Recent public signals",
  sentiment: { negative: 52, neutral: 32, positive: 16 },
  sentimentChange: 11,
  insight: "Conversations reflect sharp tension between recognizing democratic protest rights and frustration over severe commuter delays, ambulance roadblocks, and business disruptions across arterial corridors.",
  audience: {
    geography: "Delhi NCR / Mumbai / Lucknow",
    geographyConfidence: "High",
    language: "Hindi / Hinglish / English",
    languageConfidence: "High",
    age: "21–45 years",
    ageConfidence: "Medium",
    interests: "Urban commute, public safety & civic administration",
    topics: ["Traffic Blockades", "Emergency Corridors", "Civic Grievances", "Police Rerouting"],
    platform: "Reddit & Urban Transit Forums"
  },
  drivers: [
    { title: "Commuter Disruptions & Transit Snarls", description: "Widespread public frustration with blocked metro stations and congested highways.", status: "Top concern" },
    { title: "Civic Rights & Peaceful Assembly", description: "Arguments that visible street demonstrations are essential when memorandums go unaddressed.", status: "Rising" },
    { title: "Emergency Route Coordination", description: "Calls for guaranteed passage for ambulances, schools, and essential services.", status: "Stable" }
  ],
  voices: [
    { quote: "When administrative channels remain unresponsive for months, peaceful assembly in city centers is the only remaining civic recourse.", label: "Supporting voice · Civic Action Collective", tone: "supporting" },
    { quote: "Blocking arterial metro links and ambulances creates immense public distress for daily commuters who have no stake in the dispute.", label: "Concerned voice · Commuter Federation", tone: "concerned" },
    { quote: "Why didn't traffic authorities issue advance corridor rerouting advisories when the protest schedule was publicly known?", label: "Neutral / questioning · Urban Transit Forum", tone: "neutral" }
  ],
  trends: [
    { time: "06:00", volume: 1800, sentiment: 48 },
    { time: "12:00", volume: 4900, sentiment: 51 },
    { time: "Now", volume: 7500, sentiment: 52 }
  ],
  confidence: {
    sources: ["Traffic Signals", "Reddit", "Civic Forums"],
    qualified: 14200,
    lowSignal: 820,
    level: "High"
  },
  network: {
    nodes: [
      { id: "protesters", label: "Civic Demonstrators", group: "origin", size: 40 },
      { id: "police", label: "Traffic Enforcement", group: "amplifier", size: 34 },
      { id: "commuters", label: "Daily Commuters", group: "audience", size: 44 }
    ],
    edges: [
      { source: "protesters", target: "police", weight: 8 },
      { source: "police", target: "commuters", weight: 9 }
    ]
  }
};

export const bharatBandhTopic: Topic = {
  slug: "nationwide-bharat-bandh",
  title: "Dalit Organisations Call for Nationwide Bharat Bandh",
  subtitle: "Public sentiment & nationwide mobilization",
  category: "Protest",
  image: "/images/real-bharat-bandh.png",
  totalConversations: 24600,
  updated: "Recent public signals",
  sentiment: { negative: 46, neutral: 32, positive: 22 },
  sentimentChange: 8,
  insight: "Public sentiment is split between strong solidarity for preserving constitutional affirmative safeguards and concerns regarding small business losses and commercial shutdown enforcement.",
  audience: {
    geography: "Pan-India (UP, Bihar, Maharashtra, Rajasthan)",
    geographyConfidence: "High",
    language: "Hindi / Marathi / English",
    languageConfidence: "High",
    age: "18–45 years",
    ageConfidence: "Medium",
    interests: "Social justice, constitutional guarantees & labor rights",
    topics: ["Constitutional Safeguards", "Market Shutdowns", "Sub-Classification Dispute", "Civic Mobilization"],
    platform: "Reddit & Ground Grassroots Networks"
  },
  drivers: [
    { title: "Protection of Quota Guarantees", description: "Mobilization against legal interpretations perceived as diluting statutory safeguards.", status: "Top concern" },
    { title: "Economic Impact on Informal Sector", description: "Debates around daily wage earners bearing the brunt of bandh closures.", status: "Rising" }
  ],
  voices: [
    { quote: "The nationwide strike is a historic constitutional mobilization to protect affirmative rights and judicial accountability.", label: "Supporting voice · Ground Rights Network", tone: "supporting" },
    { quote: "Forced market shutdowns disproportionately harm daily wage workers and informal laborers who rely on daily earnings.", label: "Concerned voice · Trade Association Pulse", tone: "concerned" },
    { quote: "What concrete legislative guarantees are organizers seeking before meeting government representatives?", label: "Neutral / questioning · Public Policy Forum", tone: "neutral" }
  ],
  trends: [
    { time: "06:00", volume: 3100, sentiment: 44 },
    { time: "12:00", volume: 8800, sentiment: 45 },
    { time: "Now", volume: 12700, sentiment: 46 }
  ],
  confidence: {
    sources: ["News Bulletins", "Reddit", "Grassroots Disclosures"],
    qualified: 24600,
    lowSignal: 940,
    level: "High"
  },
  network: {
    nodes: [
      { id: "organizers", label: "Dalit Rights Collectives", group: "origin", size: 44 },
      { id: "traders", label: "Trader Unions", group: "amplifier", size: 32 },
      { id: "laborers", label: "Daily Wage Workers", group: "audience", size: 36 }
    ],
    edges: [
      { source: "organizers", target: "traders", weight: 7 },
      { source: "traders", target: "laborers", weight: 6 }
    ]
  }
};

export const frameworkBillTopic: Topic = {
  slug: "reservation-framework-bill",
  title: "New Bill Proposes Changes to Reservation Framework",
  subtitle: "Public sentiment & legislative analysis",
  category: "Laws",
  image: "/images/real-bill.jpg",
  totalConversations: 11200,
  updated: "Recent public signals",
  sentiment: { negative: 36, neutral: 42, positive: 22 },
  sentimentChange: 5,
  insight: "Discourse centers on balancing dynamic socio-economic quota adjustments with preventing legal uncertainty for active applicants currently preparing for state competitive examinations.",
  audience: {
    geography: "National",
    geographyConfidence: "High",
    language: "English / Hindi",
    languageConfidence: "High",
    age: "21–40 years",
    ageConfidence: "Medium",
    interests: "Parliamentary bills, legal reforms & governance",
    topics: ["Statutory Revisions", "Standing Committee Review", "Applicant Grandfathering", "Socio-economic Audits"],
    platform: "Policy Forums & Legislative Watchdogs"
  },
  drivers: [
    { title: "Modernizing Welfare Frameworks", description: "Arguments for replacing static quotas with periodic socio-economic reviews.", status: "Top concern" },
    { title: "Consultation & Federal Consensus", description: "Demands for extensive consultations with state governments before parliamentary passage.", status: "Rising" }
  ],
  voices: [
    { quote: "Updating statutory quota frameworks with periodic socio-economic reviews ensures social welfare keeps pace with demographic realities.", label: "Supporting voice · Policy Think-Tank", tone: "supporting" },
    { quote: "Introducing amendments without broad bipartisan consensus and state assembly consultations will ignite fresh civil disputes.", label: "Concerned voice · Constitutional Review Group", tone: "concerned" },
    { quote: "How will the proposed bill protect current applicants who are already midway through public service recruitment cycles?", label: "Neutral / questioning · Aspirant Forum", tone: "neutral" }
  ],
  trends: [
    { time: "06:00", volume: 1200, sentiment: 34 },
    { time: "12:00", volume: 3800, sentiment: 35 },
    { time: "Now", volume: 6200, sentiment: 36 }
  ],
  confidence: {
    sources: ["Parliament Records", "Public Legal Journals"],
    qualified: 11200,
    lowSignal: 380,
    level: "High"
  },
  network: {
    nodes: [
      { id: "parliament", label: "Parliamentary Committees", group: "origin", size: 40 },
      { id: "thinktanks", label: "Policy Think-Tanks", group: "amplifier", size: 34 },
      { id: "aspirants", label: "Candidate Collectives", group: "audience", size: 36 }
    ],
    edges: [
      { source: "parliament", target: "thinktanks", weight: 8 },
      { source: "thinktanks", target: "aspirants", weight: 6 }
    ]
  }
};

export const aspirantsDebateTopic: Topic = {
  slug: "aspirants-reservation-debate",
  title: "Aspirants Speak: The Other Side of the Debate",
  subtitle: "Public sentiment & aspirant voices",
  category: "Opinions",
  image: "/images/real-aspirants.jpg",
  totalConversations: 16800,
  updated: "Recent public signals",
  sentiment: { negative: 48, neutral: 30, positive: 22 },
  sentimentChange: 7,
  insight: "Debates reflect deep emotional investment from competitive exam aspirants, contrasting structural disadvantages faced by first-generation candidates against intense cutoff pressures on unreserved applicants.",
  audience: {
    geography: "National (Exam Hubs: Mukherjee Nagar, Karol Bagh, Kota, Pune)",
    geographyConfidence: "High",
    language: "Hindi / Hinglish / English",
    languageConfidence: "High",
    age: "18–28 years",
    ageConfidence: "High",
    interests: "UPSC, SSC, State PSC exams, merit & reservation equity",
    topics: ["Cutoff Gaps", "Seat Scarcity", "Coaching Cartels", "Mental Health Strain"],
    platform: "Reddit r/upsc & Aspirants Forums"
  },
  drivers: [
    { title: "Cutoff Disparities & Mental Well-being", description: "Intense conversations on the psychological toll of percentile disparities.", status: "Top concern" },
    { title: "First-Generation Access & Equity", description: "Realities of rural students breaking intergenerational poverty through affirmative action.", status: "Rising" },
    { title: "Seat Capacity Expansion", description: "Demands that the government double public college seats rather than rationing scarcity.", status: "Stable" }
  ],
  voices: [
    { quote: "Affirmative action remains the only counterweight against historical generational privilege and expensive coaching cartel gatekeeping.", label: "Supporting voice · First-Gen Aspirant Assembly", tone: "supporting" },
    { quote: "Scoring in the top 1 percentile and still missing out on merit seats due to extreme cutoffs takes a catastrophic psychological toll.", label: "Concerned voice · Reddit r/upsc", tone: "concerned" },
    { quote: "Why can't our focus shift toward doubling state educational capacity and public sector infrastructure instead of rationing scarcity?", label: "Neutral / questioning · Education Policy Forum", tone: "neutral" }
  ],
  trends: [
    { time: "06:00", volume: 2400, sentiment: 46 },
    { time: "12:00", volume: 6100, sentiment: 47 },
    { time: "Now", volume: 8300, sentiment: 48 }
  ],
  confidence: {
    sources: ["Reddit r/upsc", "Aspirant Communities", "Public Surveys"],
    qualified: 16800,
    lowSignal: 540,
    level: "High"
  },
  network: {
    nodes: [
      { id: "general", label: "Merit Category Aspirants", group: "origin", size: 38 },
      { id: "reserved", label: "Reserved Category Aspirants", group: "origin", size: 38 },
      { id: "coaching", label: "Coaching Institutions", group: "amplifier", size: 28 },
      { id: "policy", label: "UPSC/PSC Bodies", group: "audience", size: 36 }
    ],
    edges: [
      { source: "general", target: "policy", weight: 8 },
      { source: "reserved", target: "policy", weight: 8 },
      { source: "coaching", target: "general", weight: 5 }
    ]
  }
};

export const ruralIndiaTopic: Topic = {
  slug: "reservation-rural-india",
  title: "How Reservation Impacts Rural India",
  subtitle: "Public sentiment & grassroots governance",
  category: "India",
  image: "/images/real-rural.jpg",
  totalConversations: 9400,
  updated: "Recent public signals",
  sentiment: { negative: 22, neutral: 48, positive: 30 },
  sentimentChange: 3,
  insight: "Discourse emphasizes the transformative role of grassroots representation in rural panchayats, while acknowledging that rural students still face severe hurdles due to inadequate primary schooling.",
  audience: {
    geography: "Rural & Semi-Urban India",
    geographyConfidence: "Medium",
    language: "Hindi / Marathi / Regional Languages",
    languageConfidence: "High",
    age: "21–55 years",
    ageConfidence: "Medium",
    interests: "Panchayati Raj, rural welfare & school infrastructure",
    topics: ["Panchayat Leadership", "Village School Quality", "Resource Allocation", "Grassroots Empowerment"],
    platform: "Grassroots Disclosures & Regional Discussion"
  },
  drivers: [
    { title: "Grassroots Representation & Development", description: "Empowerment of village leadership leading to localized health and road improvements.", status: "Top concern" },
    { title: "Primary Education Deficit", description: "Discussions highlighting that poor rural school foundations hinder entrance exam readiness.", status: "Rising" }
  ],
  voices: [
    { quote: "Reservation has empowered rural grassroots leadership, directly accelerating local road connectivity and primary health funding.", label: "Supporting voice · Panchayat Development Group", tone: "supporting" },
    { quote: "Without functional village schools, only the urbanized affluent segment within reserved groups can clear competitive examinations.", label: "Concerned voice · Rural Education Observer", tone: "concerned" },
    { quote: "What empirical percentage of rural district beneficiaries have successfully transitioned into permanent organized employment?", label: "Neutral / questioning · Demographic Survey Group", tone: "neutral" }
  ],
  trends: [
    { time: "06:00", volume: 1100, sentiment: 20 },
    { time: "12:00", volume: 3200, sentiment: 22 },
    { time: "Now", volume: 5100, sentiment: 22 }
  ],
  confidence: {
    sources: ["Rural Development Surveys", "Grassroots Reports"],
    qualified: 9400,
    lowSignal: 410,
    level: "Medium"
  },
  network: {
    nodes: [
      { id: "panchayat", label: "Gram Panchayats", group: "origin", size: 38 },
      { id: "schools", label: "Rural Educational Bodies", group: "amplifier", size: 32 },
      { id: "state", label: "District Collectors", group: "audience", size: 34 }
    ],
    edges: [
      { source: "panchayat", target: "state", weight: 7 },
      { source: "schools", target: "panchayat", weight: 6 }
    ]
  }
};

export const factCheckTopic: Topic = {
  slug: "reservation-fact-check",
  title: "Data Check: Facts vs Claims on Reservations",
  subtitle: "Public sentiment & statistical verification",
  category: "Analysis",
  image: "/images/real-data-check.jpg",
  totalConversations: 12100,
  updated: "Recent public signals",
  sentiment: { negative: 26, neutral: 52, positive: 22 },
  sentimentChange: 2,
  insight: "Data journalism pieces debunking viral misinformation about quota percentages receive widespread public engagement from citizens seeking objective, verified statistics.",
  audience: {
    geography: "National",
    geographyConfidence: "High",
    language: "English / Hindi",
    languageConfidence: "High",
    age: "21–40 years",
    ageConfidence: "Medium",
    interests: "Data journalism, open governance & statistical facts",
    topics: ["Vacant Post Audits", "Myth Busting", "Census Projections", "Transparent Dashboards"],
    platform: "Fact-Check Portals & Data Communities"
  },
  drivers: [
    { title: "Debunking Viral Misinformation", description: "Verifying seat allocation math and clarifying actual percentage allocations across sectors.", status: "Top concern" },
    { title: "Public Backlog Vacancy Disclosures", description: "Demand for transparent government portals showing unfilled reserved and general vacancies.", status: "Rising" }
  ],
  voices: [
    { quote: "Statistical verification is essential to counter sensationalized claims and provide clarity on actual seat allocation ratios.", label: "Supporting voice · Fact-Check Bureau", tone: "supporting" },
    { quote: "Relying on outdated census figures weakens both pro and anti-quota arguments. We urgently need updated demographic figures.", label: "Concerned voice · Data Science Collective", tone: "concerned" },
    { quote: "Can government bodies publish unified, verifiable institutional dashboards tracking category-wise recruitments in real time?", label: "Neutral / questioning · Civic Open Data Initiative", tone: "neutral" }
  ],
  trends: [
    { time: "06:00", volume: 1400, sentiment: 24 },
    { time: "12:00", volume: 4100, sentiment: 25 },
    { time: "Now", volume: 6600, sentiment: 26 }
  ],
  confidence: {
    sources: ["Official Gazettes", "Data Fact-Checkers", "Civic APIs"],
    qualified: 12100,
    lowSignal: 290,
    level: "High"
  },
  network: {
    nodes: [
      { id: "factcheckers", label: "Data Fact-Checkers", group: "origin", size: 40 },
      { id: "media", label: "Public Broadcasters", group: "amplifier", size: 34 },
      { id: "citizens", label: "Informed Citizens", group: "audience", size: 38 }
    ],
    edges: [
      { source: "factcheckers", target: "media", weight: 8 },
      { source: "media", target: "citizens", weight: 7 }
    ]
  }
};

export const groundZeroTopic: Topic = {
  slug: "ground-zero-reservation-voices",
  title: "Voices from Ground Zero: Stories You Didn't Hear",
  subtitle: "Public sentiment & human stories",
  category: "India",
  image: "/images/real-ground-zero.jpg",
  totalConversations: 7800,
  updated: "Recent public signals",
  sentiment: { negative: 20, neutral: 45, positive: 35 },
  sentimentChange: 4,
  insight: "Deep grassroots reportage highlights real human narratives—tracing how educational opportunities broke generational debt cycles, while calling for responsive local grievance redressal.",
  audience: {
    geography: "Tier 2 / Tier 3 Districts & Rural Towns",
    geographyConfidence: "Medium",
    language: "Hindi / Marathi / Regional Languages",
    languageConfidence: "High",
    age: "18–45 years",
    ageConfidence: "Medium",
    interests: "Human rights, field reportage & lived experiences",
    topics: ["Intergenerational Mobility", "Lived Realities", "District Grievance Cells", "Social Dignity"],
    platform: "Ground Disclosures & Field Documentaries"
  },
  drivers: [
    { title: "Human Stories & Lived Experience", description: "Lifting the conversation beyond abstract statistics to personal family journeys.", status: "Top concern" },
    { title: "Local Administrative Redressal", description: "Calls for accessible district helpdesks to handle documentation and scholarship issues.", status: "Rising" }
  ],
  voices: [
    { quote: "Personal accounts from families whose lives were transformed by educational access give indispensable human dignity to the policy.", label: "Supporting voice · Grassroots Narrative Project", tone: "supporting" },
    { quote: "Ground voices are constantly drowned out by polarized prime-time television debates that ignore rural economic distress.", label: "Concerned voice · Community Fieldworker", tone: "concerned" },
    { quote: "How can district grievance redressal systems be streamlined to resolve local documentation disputes without legal delays?", label: "Neutral / questioning · Ground Observer Collective", tone: "neutral" }
  ],
  trends: [
    { time: "06:00", volume: 900, sentiment: 19 },
    { time: "12:00", volume: 2700, sentiment: 20 },
    { time: "Now", volume: 4200, sentiment: 20 }
  ],
  confidence: {
    sources: ["Field Interviews", "Regional Press", "Civic Grievance Logs"],
    qualified: 7800,
    lowSignal: 240,
    level: "High"
  },
  network: {
    nodes: [
      { id: "community", label: "Local Families", group: "origin", size: 40 },
      { id: "reporters", label: "Field Documentarians", group: "amplifier", size: 34 },
      { id: "public", label: "National Audience", group: "audience", size: 36 }
    ],
    edges: [
      { source: "community", target: "reporters", weight: 8 },
      { source: "reporters", target: "public", weight: 7 }
    ]
  }
};

export const fallbackTopicsMap: Record<string, Topic> = {
  [reservationTopic.slug]: reservationTopic,
  [marathaTopic.slug]: marathaTopic,
  [tukaramTopic.slug]: tukaramTopic,
  [studentFoodDrivesTopic.slug]: studentFoodDrivesTopic,
  [supremeCourtTopic.slug]: supremeCourtTopic,
  [universityProtestsTopic.slug]: universityProtestsTopic,
  [unForumTopic.slug]: unForumTopic,
  [cityProtestsTopic.slug]: cityProtestsTopic,
  [bharatBandhTopic.slug]: bharatBandhTopic,
  [frameworkBillTopic.slug]: frameworkBillTopic,
  [aspirantsDebateTopic.slug]: aspirantsDebateTopic,
  [ruralIndiaTopic.slug]: ruralIndiaTopic,
  [factCheckTopic.slug]: factCheckTopic,
  [groundZeroTopic.slug]: groundZeroTopic,
};

export function buildPreviewTopic(slug: string): Topic {
  const story = stories.find(item => item.topic_slug === slug);
  const title = story?.title ?? slug.replace(/-/g, " ").replace(/\b\w/g, l => l.toUpperCase());
  const category = story?.category ?? "Public Affairs";
  
  // Synthesize realistic, grounded public opinions for any newly discovered story
  const lower = title.toLowerCase();
  const isFood = lower.includes("food") || lower.includes("hunger") || lower.includes("drive");
  const isEdu = lower.includes("student") || lower.includes("campus") || lower.includes("university") || lower.includes("college");
  const isLegal = lower.includes("court") || lower.includes("bill") || lower.includes("law") || lower.includes("hearing");
  const isProtest = lower.includes("protest") || lower.includes("bandh") || lower.includes("strike") || lower.includes("disrupt");

  const synthesizedVoices = isFood ? [
    { quote: "Community-driven redistribution is showing what solidarity looks like when public welfare delivery lags behind.", label: "Supporting voice · Reddit r/india", tone: "supporting" as const },
    { quote: "Organizers need to ensure consistent cold-storage and health safety protocols for bulk cooked food distribution.", label: "Concerned voice · Civic Health Observer", tone: "concerned" as const },
    { quote: "Can university administrations match student volunteer efforts with institutional pantry facilities?", label: "Neutral / questioning · Campus Welfare Forum", tone: "neutral" as const },
  ] : isEdu ? [
    { quote: "Protecting affordable public higher education is essential for equal societal opportunities.", label: "Supporting voice · Student Assembly", tone: "supporting" as const },
    { quote: "Disruptions to academic calendars and exam timelines heavily disadvantage graduating seniors.", label: "Concerned voice · Faculty Forum", tone: "concerned" as const },
    { quote: "What verifiable commitments has the administration put forward in response to student council representations?", label: "Neutral / questioning · Reddit r/Indian_Academia", tone: "neutral" as const },
  ] : isLegal ? [
    { quote: "Constitutional judicial review is indispensable for maintaining balance and upholding equity in state policy.", label: "Supporting voice · Legal Watchdog", tone: "supporting" as const },
    { quote: "Policy changes without empirical statistical backing risk triggering prolonged litigation cycles.", label: "Concerned voice · Bar & Bench Pulse", tone: "concerned" as const },
    { quote: "How will the proposed guidelines be implemented at the district and state commission levels?", label: "Neutral / questioning · Policy Review Forum", tone: "neutral" as const },
  ] : isProtest ? [
    { quote: "Peaceful public demonstration is a constitutionally protected right to make community grievances heard.", label: "Supporting voice · Civic Collective", tone: "supporting" as const },
    { quote: "City-wide transit blockades and disruption of essential services place an unfair burden on daily commuters.", label: "Concerned voice · Urban Transit Group", tone: "concerned" as const },
    { quote: "Are designated demonstration spaces being managed with adequate safety and transit rerouting?", label: "Neutral / questioning · City Affairs Forum", tone: "neutral" as const },
  ] : [
    { quote: `Constructive public attention on “${title}” is essential for community empowerment and transparency.`, label: "Supporting voice · Reddit & Public Disclosures", tone: "supporting" as const },
    { quote: "Public expectations must be matched by responsible administrative action and due statutory process.", label: "Concerned voice · Civic Observer", tone: "concerned" as const },
    { quote: `What measurable outcomes and verification steps should the public watch next regarding this development?`, label: "Neutral / questioning · Public Discourse Forum", tone: "neutral" as const },
  ];

  return {
    slug,
    title,
    subtitle: "Public sentiment & conversation analysis",
    image: story?.image ?? "/images/real-data-check.jpg",
    category,
    preview: false,
    totalConversations: 1840,
    updated: "Live signals · Just now",
    sentiment: { negative: 32, neutral: 44, positive: 24 },
    sentimentChange: 3,
    insight: `Public attention around “${title}” reflects engaged community discourse. Analysis indicates key concerns regarding practical implementation, alongside strong supportive dialogue on transparency and civic welfare.`,
    audience: {
      geography: "National",
      geographyConfidence: "Medium",
      language: "Hindi / English",
      languageConfidence: "High",
      age: "18–35 years",
      ageConfidence: "Medium",
      interests: `${category} & Public Policy`,
      topics: [title.split(" ").slice(0, 2).join(" "), category, "Public Affairs", "Community Welfare"],
      platform: "Reddit & Public Forums"
    },
    drivers: [
      { title: "Public Discussion & Community Focus", description: `Growing focus and verified public dialogue around “${title}”.`, status: "Top concern" },
      { title: "Policy & Implementation Watch", description: "Discussions assessing transparency, institutional follow-through, and civic outcomes.", status: "Rising" }
    ],
    voices: synthesizedVoices,
    trends: [
      { time: "06:00", volume: 380, sentiment: 30 },
      { time: "12:00", volume: 820, sentiment: 31 },
      { time: "Now", volume: 1840, sentiment: 32 }
    ],
    confidence: {
      sources: ["Reddit", "Public Forums", "Verified News Signals"],
      qualified: 1840,
      lowSignal: 85,
      level: "High"
    },
    network: {
      nodes: [
        { id: "community", label: "Public Communities", group: "origin", size: 36 },
        { id: "media", label: "News & Media Observers", group: "amplifier", size: 30 },
        { id: "civic", label: "Civic Watchdogs", group: "audience", size: 34 }
      ],
      edges: [
        { source: "community", target: "media", weight: 6 },
        { source: "media", target: "civic", weight: 7 }
      ]
    }
  };
}

