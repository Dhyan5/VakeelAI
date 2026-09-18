const USE_MOCK_API = process.env.NEXT_PUBLIC_USE_MOCK_API === 'true';

const sleep = (ms) => new Promise((resolve) => setTimeout(resolve, ms));

const MOCK_ANALYSIS = {
  en: {
    facts: "The petitioner claims unpaid wages for 3 months.",
    laws: ["Labor Standards Act §12"],
    precedents: ["State v. Doe (2020)"],
    strengths: "Clear evidence of contract.",
    weaknesses: "Procedural delays.",
    nextSteps: "File a formal complaint.",
    confidence: "High",
    disclaimer: "This is a research aid, not legal advice."
  },
  hi: {
    facts: "याचिकाकर्ता ने 3 महीने के अवैतनिक वेतन का दावा किया है।",
    laws: ["श्रम मानक अधिनियम §12"],
    precedents: ["राज्य बनाम डो (2020)"],
    strengths: "अनुबंध का स्पष्ट सबूत।",
    weaknesses: "प्रक्रियात्मक देरी।",
    nextSteps: "औपचारिक शिकायत दर्ज करें।",
    confidence: "उच्च",
    disclaimer: "यह एक शोध सहायता है, कानूनी सलाह नहीं।"
  },
  kn: {
    facts: "ಅರ್ಜಿದಾರರು 3 ತಿಂಗಳ ವೇತನ ಪಾವತಿಯಾಗಿಲ್ಲ ಎಂದು ಹೇಳಿದ್ದಾರೆ.",
    laws: ["ಕಾರ್ಮಿಕ ಮಾನದಂಡಗಳ ಕಾಯಿದೆ §12"],
    precedents: ["ರಾಜ್ಯ ವಿ. ಡೋ (2020)"],
    strengths: "ಒಪ್ಪಂದದ ಸ್ಪಷ್ಟ ಸಾಕ್ಷ್ಯ.",
    weaknesses: "ಕಾರ್ಯವಿಧಾನದ ವಿಳಂಬ.",
    nextSteps: "ಔಪಚಾರಿಕ ದೂರು ಸಲ್ಲಿಸಿ.",
    confidence: "ಹೆಚ್ಚು",
    disclaimer: "ಇದು ಸಂಶೋಧನಾ ಸಹಾಯವಾಗಿದೆ, ಕಾನೂನು ಸಲಹೆಯಲ್ಲ."
  }
};

export const submitCaseText = async (text, lang) => {
  if (!USE_MOCK_API) {
    // Real API call here
    // return fetch('/api/case', ...).then(res => res.json());
  }
  await sleep(1500); // Simulate network
  return { id: "case_123", ...MOCK_ANALYSIS[lang || 'en'] };
};

export const getCaseHistory = async () => {
  if (!USE_MOCK_API) {
    // return fetch('/api/history').then(res => res.json());
  }
  await sleep(500);
  return [
    { id: "1", title: "Wage Dispute", date: "2026-09-17" },
    { id: "2", title: "Property Case", date: "2026-09-15" }
  ];
};
