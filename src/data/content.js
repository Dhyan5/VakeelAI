/**
 * VakeelAI - Multilingual Content & Mock Data
 * Supports: English (en), Hindi (hi), Kannada (kn)
 */

// ─── Language Config ─────────────────────────────────────────────────────────
export const LANGUAGES = [
  { code: 'en', label: 'English', native: 'English', flag: '🇬🇧', ttsCode: 'en-IN' },
  { code: 'hi', label: 'Hindi', native: 'हिंदी', flag: '🇮🇳', ttsCode: 'hi-IN' },
  { code: 'kn', label: 'Kannada', native: 'ಕನ್ನಡ', flag: '🇮🇳', ttsCode: 'kn-IN' },
];

// ─── UI Translations ──────────────────────────────────────────────────────────
export const UI_TEXT = {
  en: {
    appName: 'VakeelAI',
    tagline: 'Your AI-Powered Legal Assistant',
    navChat: 'Chat',
    navDocuments: 'Documents',
    navHistory: 'History',
    greeting: 'Hello! I am VakeelAI',
    greetingSubtitle: 'Your intelligent legal assistant powered by AI. Ask me anything about legal matters, upload documents for analysis, or explore common legal scenarios.',
    inputPlaceholder: 'Ask a legal question or describe your situation...',
    uploadTitle: 'Upload Legal Document',
    uploadSubtitle: 'Drag & drop your PDF or Word document here, or click to browse',
    uploadFormats: 'Supported: PDF, DOC, DOCX (Max 10MB)',
    analyzeBtn: 'Analyze Document',
    clearBtn: 'Clear',
    sendBtn: 'Send',
    analyzing: 'Analyzing document...',
    analysisComplete: 'Analysis complete',
    speakBtn: 'Listen',
    speaking: 'Speaking...',
    suggestions: [
      'What are my tenant rights?',
      'How to file a consumer complaint?',
      'Explain property transfer laws',
      'What is anticipatory bail?',
      'Rights during police arrest',
    ],
    documentUploaded: 'Document uploaded successfully',
    disclaimer: 'VakeelAI provides general legal information only. For legal advice specific to your situation, please consult a qualified lawyer.',
    processingSteps: [
      'Extracting text content...',
      'Identifying legal clauses...',
      'Cross-referencing Indian law...',
      'Generating analysis report...',
    ],
    tabs: {
      chat: 'Legal Chat',
      upload: 'Document Analysis',
    },
  },
  hi: {
    appName: 'वकील AI',
    tagline: 'आपका AI-संचालित कानूनी सहायक',
    navChat: 'चैट',
    navDocuments: 'दस्तावेज़',
    navHistory: 'इतिहास',
    greeting: 'नमस्ते! मैं वकील AI हूँ',
    greetingSubtitle: 'आपका बुद्धिमान कानूनी सहायक। कानूनी मामलों के बारे में कुछ भी पूछें, दस्तावेज़ अपलोड करें या सामान्य कानूनी परिदृश्यों का पता लगाएं।',
    inputPlaceholder: 'कोई कानूनी प्रश्न पूछें या अपनी स्थिति बताएं...',
    uploadTitle: 'कानूनी दस्तावेज़ अपलोड करें',
    uploadSubtitle: 'अपना PDF या Word दस्तावेज़ यहाँ खींचें और छोड़ें, या ब्राउज़ करने के लिए क्लिक करें',
    uploadFormats: 'समर्थित: PDF, DOC, DOCX (अधिकतम 10MB)',
    analyzeBtn: 'दस्तावेज़ विश्लेषण करें',
    clearBtn: 'साफ़ करें',
    sendBtn: 'भेजें',
    analyzing: 'दस्तावेज़ का विश्लेषण हो रहा है...',
    analysisComplete: 'विश्लेषण पूर्ण',
    speakBtn: 'सुनें',
    speaking: 'बोल रहा है...',
    suggestions: [
      'किराएदार के अधिकार क्या हैं?',
      'उपभोक्ता शिकायत कैसे दर्ज करें?',
      'संपत्ति हस्तांतरण कानून',
      'अग्रिम जमानत क्या है?',
      'गिरफ्तारी के दौरान अधिकार',
    ],
    documentUploaded: 'दस्तावेज़ सफलतापूर्वक अपलोड हुआ',
    disclaimer: 'वकील AI केवल सामान्य कानूनी जानकारी प्रदान करता है। अपनी स्थिति के लिए विशिष्ट कानूनी सलाह के लिए, कृपया एक योग्य वकील से परामर्श करें।',
    processingSteps: [
      'पाठ सामग्री निकाली जा रही है...',
      'कानूनी धाराएँ पहचानी जा रही हैं...',
      'भारतीय कानून के साथ मिलान हो रहा है...',
      'विश्लेषण रिपोर्ट तैयार हो रही है...',
    ],
    tabs: {
      chat: 'कानूनी चैट',
      upload: 'दस्तावेज़ विश्लेषण',
    },
  },
  kn: {
    appName: 'ವಕೀಲ್ AI',
    tagline: 'ನಿಮ್ಮ AI-ಚಾಲಿತ ಕಾನೂನು ಸಹಾಯಕ',
    navChat: 'ಚಾಟ್',
    navDocuments: 'ದಾಖಲೆಗಳು',
    navHistory: 'ಇತಿಹಾಸ',
    greeting: 'ನಮಸ್ಕಾರ! ನಾನು ವಕೀಲ್ AI',
    greetingSubtitle: 'ನಿಮ್ಮ ಬುದ್ಧಿವಂತ ಕಾನೂನು ಸಹಾಯಕ. ಕಾನೂನು ವಿಷಯಗಳ ಬಗ್ಗೆ ಏನಾದರೂ ಕೇಳಿ, ದಾಖಲೆಗಳನ್ನು ಅಪ್‌ಲೋಡ್ ಮಾಡಿ ಅಥವಾ ಸಾಮಾನ್ಯ ಕಾನೂನು ಸನ್ನಿವೇಶಗಳನ್ನು ಅನ್ವೇಷಿಸಿ.',
    inputPlaceholder: 'ಕಾನೂನು ಪ್ರಶ್ನೆ ಕೇಳಿ ಅಥವಾ ನಿಮ್ಮ ಪರಿಸ್ಥಿತಿ ವಿವರಿಸಿ...',
    uploadTitle: 'ಕಾನೂನು ದಾಖಲೆ ಅಪ್‌ಲೋಡ್ ಮಾಡಿ',
    uploadSubtitle: 'ನಿಮ್ಮ PDF ಅಥವಾ Word ದಾಖಲೆಯನ್ನು ಇಲ್ಲಿ ಎಳೆದು ಬಿಡಿ, ಅಥವಾ ಬ್ರೌಸ್ ಮಾಡಲು ಕ್ಲಿಕ್ ಮಾಡಿ',
    uploadFormats: 'ಬೆಂಬಲಿತ: PDF, DOC, DOCX (ಗರಿಷ್ಠ 10MB)',
    analyzeBtn: 'ದಾಖಲೆ ವಿಶ್ಲೇಷಿಸಿ',
    clearBtn: 'ತೆರವುಗೊಳಿಸಿ',
    sendBtn: 'ಕಳುಹಿಸಿ',
    analyzing: 'ದಾಖಲೆ ವಿಶ್ಲೇಷಿಸಲಾಗುತ್ತಿದೆ...',
    analysisComplete: 'ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣ',
    speakBtn: 'ಕೇಳಿ',
    speaking: 'ಮಾತನಾಡುತ್ತಿದೆ...',
    suggestions: [
      'ಬಾಡಿಗೆದಾರರ ಹಕ್ಕುಗಳೇನು?',
      'ಗ್ರಾಹಕ ದೂರು ಹೇಗೆ ಸಲ್ಲಿಸುವುದು?',
      'ಆಸ್ತಿ ವರ್ಗಾವಣೆ ಕಾನೂನು',
      'ಮುಂಗಡ ಜಾಮೀನು ಎಂದರೇನು?',
      'ಬಂಧನದ ಸಮಯದಲ್ಲಿ ಹಕ್ಕುಗಳು',
    ],
    documentUploaded: 'ದಾಖಲೆ ಯಶಸ್ವಿಯಾಗಿ ಅಪ್‌ಲೋಡ್ ಆಯಿತು',
    disclaimer: 'ವಕೀಲ್ AI ಕೇವಲ ಸಾಮಾನ್ಯ ಕಾನೂನು ಮಾಹಿತಿ ಒದಗಿಸುತ್ತದೆ. ನಿಮ್ಮ ಪರಿಸ್ಥಿತಿಗೆ ನಿರ್ದಿಷ್ಟ ಕಾನೂನು ಸಲಹೆಗಾಗಿ, ದಯವಿಟ್ಟು ಅರ್ಹ ವಕೀಲರನ್ನು ಸಂಪರ್ಕಿಸಿ.',
    processingSteps: [
      'ಪಠ್ಯ ವಿಷಯ ಹೊರತೆಗೆಯಲಾಗುತ್ತಿದೆ...',
      'ಕಾನೂನು ಷರತ್ತುಗಳನ್ನು ಗುರುತಿಸಲಾಗುತ್ತಿದೆ...',
      'ಭಾರತೀಯ ಕಾನೂನಿನೊಂದಿಗೆ ಹೋಲಿಸಲಾಗುತ್ತಿದೆ...',
      'ವಿಶ್ಲೇಷಣಾ ವರದಿ ರಚಿಸಲಾಗುತ್ತಿದೆ...',
    ],
    tabs: {
      chat: 'ಕಾನೂನು ಚಾಟ್',
      upload: 'ದಾಖಲೆ ವಿಶ್ಲೇಷಣೆ',
    },
  },
};

// ─── Mock AI Responses ────────────────────────────────────────────────────────
export const MOCK_RESPONSES = {
  en: {
    greetings: [
      "Welcome! I'm VakeelAI, your AI-powered legal assistant. I can help you understand your legal rights, analyze documents, and guide you through complex legal situations under Indian law. What can I assist you with today?",
    ],
    tenantRights: "Under the Rent Control Act and various state tenancy laws in India, tenants have several key rights:\n\n• **Right to a written agreement**: Always insist on a registered rent agreement.\n• **Protection from arbitrary eviction**: Landlords cannot evict you without proper legal notice (typically 15–30 days).\n• **Right to essential services**: Landlords cannot cut off water, electricity, or other utilities as a means of harassment.\n• **Right to privacy**: Your landlord must give advance notice before entering the premises.\n• **Security deposit limits**: Maximum 2–3 months' rent in most states.\n\nIf your landlord violates any of these rights, you may file a complaint with the Rent Control Authority or approach a civil court.",
    consumerComplaint: "Filing a consumer complaint in India is a structured process under the Consumer Protection Act, 2019:\n\n**Step 1 – Notify the Seller**: Send a written notice to the seller/service provider describing the defect or deficiency.\n\n**Step 2 – Choose the Right Forum**:\n• District Consumer Commission: Claims up to ₹50 lakhs\n• State Consumer Commission: ₹50 lakhs – ₹2 crore\n• National Consumer Commission: Above ₹2 crore\n\n**Step 3 – File the Complaint**: You can file online at edaakhil.nic.in or visit the commission office. Include bills, warranties, and correspondence.\n\n**Step 4 – Pay the Fee**: Nominal fee of ₹100–₹5,000 depending on claim value.\n\nYou can also seek relief including refund, replacement, compensation for mental agony, and litigation costs.",
    bail: "Anticipatory Bail (Pre-arrest bail) under Section 438 of the CrPC is a legal provision allowing a person to seek bail in anticipation of an arrest:\n\n**Key Points**:\n• Filed in Sessions Court or High Court before arrest\n• Court considers the nature of the accusation, antecedents of the applicant, and possibility of fleeing from justice\n• Once granted, if the police arrest you, you are released immediately on bail\n\n**Conditions typically imposed**:\n• Must make yourself available for interrogation\n• Cannot leave India without court permission\n• Must surrender your passport\n• Cannot tamper with evidence or influence witnesses\n\n**Recent SC Ruling**: The Supreme Court has held that anticipatory bail does not expire at the time of filing the chargesheet.",
    arrest: "Under Articles 20, 21, and 22 of the Indian Constitution and the CrPC, you have the following rights during arrest:\n\n• **Right to know the reason**: Police must tell you why you are being arrested.\n• **Right to an advocate**: You can consult and be defended by a legal practitioner.\n• **Right to be produced before a Magistrate**: Within 24 hours of arrest (excluding travel time).\n• **Right against self-incrimination**: You cannot be forced to be a witness against yourself.\n• **Right to inform family/friend**: Police must inform a relative or friend about your arrest.\n• **No third-degree**: Any torture or inhumane treatment is illegal under Section 49 CrPC.\n\n⚠️ **Important**: Women can only be arrested by female police officers, and typically only between 6 AM and 6 PM.",
    property: "Property transfer in India is governed primarily by the Transfer of Property Act, 1882. Key modes of transfer include:\n\n**Sale**: Most common form; requires a registered Sale Deed at the Sub-Registrar's office. Stamp duty (5–8% of property value) applies.\n\n**Gift**: Transfer by Gift Deed; must be registered if it's immovable property worth above ₹100.\n\n**Will**: Takes effect after death; subject to succession laws (Hindu Succession Act, Indian Succession Act).\n\n**Mutation**: After transfer, property records must be updated (mutated) in the local municipal/revenue authority.\n\n**Important Checks**:\n• Verify title chain for minimum 30 years\n• Check for encumbrances at Sub-Registrar's office\n• Obtain Encumbrance Certificate (EC)\n• Verify RERA registration for under-construction properties",
    documentAnalysis: "📄 **Document Analysis Complete**\n\nBased on my analysis of the uploaded document, I've identified the following key legal issues:\n\n**Document Type**: Rental Agreement / Lease Deed\n\n**⚠️ Red Flags Identified**:\n1. Clause 7 contains an **arbitrary eviction clause** that violates the Rent Control Act — landlord claims right to evict with only 7 days notice, which is legally insufficient.\n2. **Security deposit clause** demands 6 months advance rent — exceeds the legal limit of 2 months in Karnataka.\n3. **Unilateral rent increase clause** (Clause 12) — allows landlord to increase rent without tenant consent, which is invalid.\n\n**✅ Recommended Actions**:\n• Negotiate removal of Clause 7 and replace with standard 30-day notice period\n• Insist on security deposit limit as per Karnataka Rent Control Act\n• Add a mutual consent clause for rent revision\n• Get the agreement registered at Sub-Registrar's office for legal validity\n\n**Applicable Laws**: Karnataka Rent Control Act 2001, Transfer of Property Act 1882, Indian Contract Act 1872",
    default: "That's an important legal question. Under Indian law, the answer depends on several factors including your specific circumstances, jurisdiction, and applicable statutes. I recommend consulting with a qualified advocate for personalized advice. However, here's what you should generally know about this matter:\n\nThe Indian legal system provides remedies through civil courts, consumer forums, and various tribunals depending on the nature of your case. You may also file a complaint with the relevant regulatory authority. Would you like me to elaborate on any specific aspect of this matter?",
  },
  hi: {
    greetings: [
      "नमस्ते! मैं वकील AI हूँ, आपका AI-संचालित कानूनी सहायक। मैं आपको भारतीय कानून के तहत आपके कानूनी अधिकारों को समझने, दस्तावेज़ों का विश्लेषण करने और जटिल कानूनी स्थितियों में मार्गदर्शन करने में मदद कर सकता हूँ। आज मैं आपकी क्या सहायता कर सकता हूँ?",
    ],
    tenantRights: "भारत में किराया नियंत्रण अधिनियम और विभिन्न राज्य किरायेदारी कानूनों के तहत, किराएदारों के पास कई महत्वपूर्ण अधिकार हैं:\n\n• **लिखित समझौते का अधिकार**: हमेशा पंजीकृत किराया समझौते पर जोर दें।\n• **मनमाने बेदखली से सुरक्षा**: मकान मालिक उचित कानूनी नोटिस (आमतौर पर 15-30 दिन) के बिना आपको नहीं निकाल सकता।\n• **आवश्यक सेवाओं का अधिकार**: मकान मालिक उत्पीड़न के साधन के रूप में पानी, बिजली या अन्य सुविधाएं नहीं काट सकता।\n• **गोपनीयता का अधिकार**: आपके मकान मालिक को परिसर में प्रवेश करने से पहले अग्रिम नोटिस देना होगा।\n• **सुरक्षा जमा सीमाएं**: अधिकांश राज्यों में अधिकतम 2-3 महीने का किराया।\n\nयदि आपका मकान मालिक इनमें से किसी भी अधिकार का उल्लंघन करता है, तो आप किराया नियंत्रण प्राधिकरण के पास शिकायत दर्ज कर सकते हैं।",
    consumerComplaint: "उपभोक्ता संरक्षण अधिनियम, 2019 के तहत भारत में उपभोक्ता शिकायत दर्ज करना एक व्यवस्थित प्रक्रिया है:\n\n**चरण 1 – विक्रेता को सूचित करें**: विक्रेता/सेवा प्रदाता को दोष या कमी का वर्णन करते हुए लिखित नोटिस भेजें।\n\n**चरण 2 – सही मंच चुनें**:\n• जिला उपभोक्ता आयोग: ₹50 लाख तक के दावे\n• राज्य उपभोक्ता आयोग: ₹50 लाख - ₹2 करोड़\n• राष्ट्रीय उपभोक्ता आयोग: ₹2 करोड़ से अधिक\n\n**चरण 3 – शिकायत दर्ज करें**: आप edaakhil.nic.in पर ऑनलाइन फाइल कर सकते हैं या आयोग कार्यालय जा सकते हैं।\n\n**चरण 4 – शुल्क का भुगतान करें**: दावे के मूल्य के आधार पर ₹100-₹5,000 का मामूली शुल्क।",
    bail: "CrPC की धारा 438 के तहत अग्रिम जमानत (गिरफ्तारी पूर्व जमानत) एक कानूनी प्रावधान है जो किसी व्यक्ति को गिरफ्तारी की आशंका में जमानत मांगने की अनुमति देता है:\n\n**मुख्य बिंदु**:\n• गिरफ्तारी से पहले सत्र न्यायालय या उच्च न्यायालय में दायर किया जाता है\n• न्यायालय आरोप की प्रकृति, आवेदक के पूर्ववृत्त और न्याय से भागने की संभावना पर विचार करता है\n• एक बार मंजूर होने पर, यदि पुलिस आपको गिरफ्तार करती है, तो आप तुरंत जमानत पर रिहा हो जाते हैं\n\n**आमतौर पर लगाई जाने वाली शर्तें**:\n• पूछताछ के लिए उपलब्ध रहना होगा\n• न्यायालय की अनुमति के बिना भारत नहीं छोड़ सकते\n• पासपोर्ट जमा करना होगा",
    arrest: "भारतीय संविधान के अनुच्छेद 20, 21 और 22 और CrPC के तहत, गिरफ्तारी के दौरान आपके निम्नलिखित अधिकार हैं:\n\n• **कारण जानने का अधिकार**: पुलिस को आपको बताना होगा कि आपको क्यों गिरफ्तार किया जा रहा है।\n• **वकील का अधिकार**: आप एक कानूनी व्यवसायी से परामर्श कर सकते हैं और उनके द्वारा बचाव करवा सकते हैं।\n• **मजिस्ट्रेट के समक्ष पेश होने का अधिकार**: गिरफ्तारी के 24 घंटे के भीतर।\n• **आत्म-दोषारोपण के विरुद्ध अधिकार**: आपको अपने विरुद्ध गवाह बनने के लिए मजबूर नहीं किया जा सकता।\n• **परिवार/मित्र को सूचित करने का अधिकार**: पुलिस को आपके किसी संबंधी या मित्र को गिरफ्तारी की जानकारी देनी होगी।",
    property: "भारत में संपत्ति हस्तांतरण मुख्य रूप से संपत्ति हस्तांतरण अधिनियम, 1882 द्वारा नियंत्रित होता है। हस्तांतरण के प्रमुख तरीकों में शामिल हैं:\n\n**बिक्री**: सबसे सामान्य रूप; उप-पंजीयक कार्यालय में पंजीकृत बिक्री विलेख की आवश्यकता है।\n\n**उपहार**: उपहार विलेख द्वारा हस्तांतरण; यदि यह ₹100 से अधिक मूल्य की अचल संपत्ति है तो इसे पंजीकृत करना होगा।\n\n**वसीयत**: मृत्यु के बाद प्रभावी; उत्तराधिकार कानूनों के अधीन।\n\n**म्यूटेशन**: हस्तांतरण के बाद, स्थानीय नगरपालिका/राजस्व प्राधिकरण में संपत्ति रिकॉर्ड अपडेट करना होगा।",
    documentAnalysis: "📄 **दस्तावेज़ विश्लेषण पूर्ण**\n\nअपलोड किए गए दस्तावेज़ के मेरे विश्लेषण के आधार पर, मैंने निम्नलिखित महत्वपूर्ण कानूनी मुद्दों की पहचान की है:\n\n**दस्तावेज़ प्रकार**: किराया समझौता / पट्टा विलेख\n\n**⚠️ पहचाने गए लाल झंडे**:\n1. धारा 7 में एक **मनमाना बेदखली खंड** है जो किराया नियंत्रण अधिनियम का उल्लंघन करता है।\n2. **सुरक्षा जमा खंड** 6 महीने का अग्रिम किराया मांगता है — कर्नाटक में 2 महीने की कानूनी सीमा से अधिक।\n3. **एकतरफा किराया वृद्धि खंड** (धारा 12) — किराएदार की सहमति के बिना किराया बढ़ाने की अनुमति देता है।\n\n**✅ अनुशंसित कार्रवाई**:\n• धारा 7 को हटाने पर बातचीत करें और 30 दिन के नोटिस अवधि से बदलें\n• कर्नाटक किराया नियंत्रण अधिनियम के अनुसार सुरक्षा जमा सीमा पर जोर दें\n• किराया संशोधन के लिए आपसी सहमति खंड जोड़ें",
    default: "यह एक महत्वपूर्ण कानूनी प्रश्न है। भारतीय कानून के तहत, उत्तर आपकी विशिष्ट परिस्थितियों, क्षेत्राधिकार और लागू कानूनों सहित कई कारकों पर निर्भर करता है। मैं व्यक्तिगत सलाह के लिए एक योग्य अधिवक्ता से परामर्श करने की सलाह देता हूँ। क्या आप इस मामले के किसी विशिष्ट पहलू के बारे में अधिक जानकारी चाहेंगे?",
  },
  kn: {
    greetings: [
      "ನಮಸ್ಕಾರ! ನಾನು ವಕೀಲ್ AI, ನಿಮ್ಮ AI-ಚಾಲಿತ ಕಾನೂನು ಸಹಾಯಕ. ಭಾರತೀಯ ಕಾನೂನಿನ ಅಡಿ ನಿಮ್ಮ ಕಾನೂನು ಹಕ್ಕುಗಳನ್ನು ಅರ್ಥಮಾಡಿಕೊಳ್ಳಲು, ದಾಖಲೆಗಳನ್ನು ವಿಶ್ಲೇಷಿಸಲು ಮತ್ತು ಸಂಕೀರ್ಣ ಕಾನೂನು ಸಂದರ್ಭಗಳಲ್ಲಿ ಮಾರ್ಗದರ್ಶನ ನೀಡಲು ನಾನು ಸಹಾಯ ಮಾಡಬಲ್ಲೆ. ಇಂದು ನಾನು ನಿಮಗೆ ಹೇಗೆ ಸಹಾಯ ಮಾಡಬಹುದು?",
    ],
    tenantRights: "ಭಾರತದಲ್ಲಿ ಬಾಡಿಗೆ ನಿಯಂತ್ರಣ ಕಾಯ್ದೆ ಮತ್ತು ವಿವಿಧ ರಾಜ್ಯ ಗೃಹ ನಿಯಮಗಳ ಅಡಿ, ಬಾಡಿಗೆದಾರರಿಗೆ ಹಲವಾರು ಪ್ರಮುಖ ಹಕ್ಕುಗಳಿವೆ:\n\n• **ಲಿಖಿತ ಒಪ್ಪಂದದ ಹಕ್ಕು**: ನೋಂದಾಯಿತ ಬಾಡಿಗೆ ಒಪ್ಪಂದದ ಮೇಲೆ ಯಾವಾಗಲೂ ಒತ್ತಾಯಿಸಿ.\n• **ಅನಿಯಂತ್ರಿತ ಹೊರಹಾಕುವಿಕೆಯಿಂದ ರಕ್ಷಣೆ**: ಸೂಕ್ತ ಕಾನೂನು ನೋಟಿಸ್ (ಸಾಮಾನ್ಯವಾಗಿ 15-30 ದಿನ) ಇಲ್ಲದೆ ಮನೆ ಮಾಲೀಕರು ನಿಮ್ಮನ್ನು ಹೊರಹಾಕಲು ಸಾಧ್ಯವಿಲ್ಲ.\n• **ಅಗತ್ಯ ಸೇವೆಗಳ ಹಕ್ಕು**: ಮನೆ ಮಾಲೀಕರು ಕಿರುಕುಳದ ಸಾಧನವಾಗಿ ನೀರು, ವಿದ್ಯುತ್ ಅಥವಾ ಇತರ ಸೌಲಭ್ಯಗಳನ್ನು ಕಡಿತಗೊಳಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ.\n• **ಗೋಪ್ಯತೆಯ ಹಕ್ಕು**: ಆವರಣಕ್ಕೆ ಪ್ರವೇಶಿಸುವ ಮೊದಲು ಮನೆ ಮಾಲೀಕರು ಮುಂಚಿತ ಸೂಚನೆ ನೀಡಬೇಕು.\n• **ಭದ್ರತಾ ಠೇವಣಿ ಮಿತಿಗಳು**: ಹೆಚ್ಚಿನ ರಾಜ್ಯಗಳಲ್ಲಿ ಗರಿಷ್ಠ 2-3 ತಿಂಗಳ ಬಾಡಿಗೆ.",
    consumerComplaint: "ಗ್ರಾಹಕ ಸಂರಕ್ಷಣಾ ಕಾಯ್ದೆ, 2019 ರ ಅಡಿ ಭಾರತದಲ್ಲಿ ಗ್ರಾಹಕ ದೂರು ಸಲ್ಲಿಸುವುದು ಒಂದು ರಚನಾತ್ಮಕ ಪ್ರಕ್ರಿಯೆ:\n\n**ಹಂತ 1 – ಮಾರಾಟಗಾರರಿಗೆ ಸೂಚಿಸಿ**: ದೋಷ ಅಥವಾ ಲೋಪವನ್ನು ವಿವರಿಸುವ ಲಿಖಿತ ನೋಟಿಸ್ ಕಳುಹಿಸಿ.\n\n**ಹಂತ 2 – ಸರಿಯಾದ ವೇದಿಕೆ ಆಯ್ಕೆ**:\n• ಜಿಲ್ಲಾ ಗ್ರಾಹಕ ಆಯೋಗ: ₹50 ಲಕ್ಷದವರೆಗಿನ ಹಕ್ಕು\n• ರಾಜ್ಯ ಗ್ರಾಹಕ ಆಯೋಗ: ₹50 ಲಕ್ಷ – ₹2 ಕೋಟಿ\n• ರಾಷ್ಟ್ರೀಯ ಗ್ರಾಹಕ ಆಯೋಗ: ₹2 ಕೋಟಿಗಿಂತ ಹೆಚ್ಚು\n\n**ಹಂತ 3 – ದೂರು ಸಲ್ಲಿಸಿ**: edaakhil.nic.in ನಲ್ಲಿ ಆನ್‌ಲೈನ್‌ನಲ್ಲಿ ಸಲ್ಲಿಸಬಹುದು.",
    bail: "CrPC ಯ ಸೆಕ್ಷನ್ 438 ರ ಅಡಿ ಮುಂಗಡ ಜಾಮೀನು (ಬಂಧನ ಪೂರ್ವ ಜಾಮೀನು) ಒಂದು ಕಾನೂನು ನಿಬಂಧನೆಯಾಗಿದ್ದು, ಒಬ್ಬ ವ್ಯಕ್ತಿಯು ಬಂಧನದ ನಿರೀಕ್ಷೆಯಲ್ಲಿ ಜಾಮೀನು ಕೋರಬಹುದಾಗಿದೆ:\n\n**ಪ್ರಮುಖ ಅಂಶಗಳು**:\n• ಬಂಧನದ ಮೊದಲು ಸೆಷನ್ಸ್ ಕೋರ್ಟ್ ಅಥವಾ ಹೈಕೋರ್ಟ್‌ನಲ್ಲಿ ಸಲ್ಲಿಸಲಾಗುತ್ತದೆ\n• ಕೋರ್ಟ್ ಆರೋಪದ ಸ್ವರೂಪ, ಅರ್ಜಿದಾರರ ಹಿನ್ನೆಲೆ ಮತ್ತು ನ್ಯಾಯದಿಂದ ಓಡಿಹೋಗುವ ಸಾಧ್ಯತೆಯನ್ನು ಪರಿಗಣಿಸುತ್ತದೆ\n• ಒಮ್ಮೆ ಮಂಜೂರಾದರೆ, ಪೊಲೀಸರು ನಿಮ್ಮನ್ನು ಬಂಧಿಸಿದರೆ, ನೀವು ತಕ್ಷಣ ಜಾಮೀನಿನ ಮೇಲೆ ಬಿಡುಗಡೆ ಆಗುತ್ತೀರಿ",
    arrest: "ಭಾರತೀಯ ಸಂವಿಧಾನದ ಅನುಚ್ಛೇದಗಳು 20, 21 ಮತ್ತು 22 ಮತ್ತು CrPC ಅಡಿ, ಬಂಧನದ ಸಮಯದಲ್ಲಿ ನಿಮಗೆ ಈ ಕೆಳಗಿನ ಹಕ್ಕುಗಳಿವೆ:\n\n• **ಕಾರಣ ತಿಳಿಯುವ ಹಕ್ಕು**: ನಿಮ್ಮನ್ನು ಏಕೆ ಬಂಧಿಸಲಾಗುತ್ತಿದೆ ಎಂದು ಪೊಲೀಸರು ಹೇಳಬೇಕು.\n• **ವಕೀಲರ ಹಕ್ಕು**: ನೀವು ಕಾನೂನು ವೃತ್ತಿಪರರನ್ನು ಸಮಾಲೋಚಿಸಬಹುದು.\n• **ಮ್ಯಾಜಿಸ್ಟ್ರೇಟ್ ಮುಂದೆ ಹಾಜರುಪಡಿಸುವ ಹಕ್ಕು**: ಬಂಧನದ 24 ಗಂಟೆಗಳ ಒಳಗೆ.\n• **ಸ್ವಯಂ-ದೋಷಾರೋಪಣೆ ವಿರುದ್ಧ ಹಕ್ಕು**: ನಿಮ್ಮ ವಿರುದ್ಧ ಸಾಕ್ಷಿಯಾಗಲು ನಿಮ್ಮನ್ನು ಒತ್ತಾಯಿಸಲು ಸಾಧ್ಯವಿಲ್ಲ.\n• **ಕುಟುಂಬ/ಸ್ನೇಹಿತರಿಗೆ ತಿಳಿಸುವ ಹಕ್ಕು**: ಬಂಧನದ ಬಗ್ಗೆ ಸಂಬಂಧಿ ಅಥವಾ ಸ್ನೇಹಿತರಿಗೆ ತಿಳಿಸಬೇಕು.",
    property: "ಭಾರತದಲ್ಲಿ ಆಸ್ತಿ ವರ್ಗಾವಣೆಯನ್ನು ಮುಖ್ಯವಾಗಿ ಆಸ್ತಿ ವರ್ಗಾವಣೆ ಕಾಯ್ದೆ, 1882 ನಿಯಂತ್ರಿಸುತ್ತದೆ:\n\n**ಮಾರಾಟ**: ಅತ್ಯಂತ ಸಾಮಾನ್ಯ ರೂಪ; ಉಪ-ನೋಂದಣಾಧಿಕಾರಿ ಕಚೇರಿಯಲ್ಲಿ ನೋಂದಾಯಿತ ಮಾರಾಟ ಪತ್ರ ಅಗತ್ಯ.\n\n**ಉಡುಗೊರೆ**: ಉಡುಗೊರೆ ಪತ್ರದ ಮೂಲಕ ವರ್ಗಾವಣೆ; ₹100ಕ್ಕಿಂತ ಹೆಚ್ಚಿನ ಮೌಲ್ಯದ ಸ್ಥಿರ ಆಸ್ತಿಯಾದರೆ ನೋಂದಾಯಿಸಬೇಕು.\n\n**ವಿಲ್**: ಮರಣದ ನಂತರ ಜಾರಿಗೆ ಬರುತ್ತದೆ; ಉತ್ತರಾಧಿಕಾರ ಕಾನೂನುಗಳಿಗೆ ಅನುಸಾರವಾಗಿ.\n\n**ಮ್ಯೂಟೇಶನ್**: ವರ್ಗಾವಣೆಯ ನಂತರ, ಸ್ಥಳೀಯ ಪಾಲಿಕೆ/ಕಂದಾಯ ಪ್ರಾಧಿಕಾರದಲ್ಲಿ ಆಸ್ತಿ ದಾಖಲೆಗಳನ್ನು ನವೀಕರಿಸಬೇಕು.",
    documentAnalysis: "📄 **ದಾಖಲೆ ವಿಶ್ಲೇಷಣೆ ಪೂರ್ಣ**\n\nಅಪ್‌ಲೋಡ್ ಮಾಡಿದ ದಾಖಲೆಯ ನನ್ನ ವಿಶ್ಲೇಷಣೆಯ ಆಧಾರದಲ್ಲಿ, ಈ ಕೆಳಗಿನ ಪ್ರಮುಖ ಕಾನೂನು ಸಮಸ್ಯೆಗಳನ್ನು ಗುರುತಿಸಿದ್ದೇನೆ:\n\n**ದಾಖಲೆ ಪ್ರಕಾರ**: ಬಾಡಿಗೆ ಒಪ್ಪಂದ / ಗುತ್ತಿಗೆ ಪತ್ರ\n\n**⚠️ ಗುರುತಿಸಲಾದ ಸಮಸ್ಯೆಗಳು**:\n1. ಷರತ್ತು 7 ಬಾಡಿಗೆ ನಿಯಂತ್ರಣ ಕಾಯ್ದೆಯನ್ನು ಉಲ್ಲಂಘಿಸುವ **ಅನಿಯಂತ್ರಿತ ಹೊರಹಾಕುವಿಕೆ ಷರತ್ತನ್ನು** ಒಳಗೊಂಡಿದೆ.\n2. **ಭದ್ರತಾ ಠೇವಣಿ ಷರತ್ತು** 6 ತಿಂಗಳ ಮುಂಗಡ ಬಾಡಿಗೆ ಕೇಳುತ್ತದೆ — ಕರ್ನಾಟಕದಲ್ಲಿ 2 ತಿಂಗಳ ಕಾನೂನು ಮಿತಿಯನ್ನು ಮೀರುತ್ತದೆ.\n3. **ಏಕಪಕ್ಷೀಯ ಬಾಡಿಗೆ ಹೆಚ್ಚಳ ಷರತ್ತು** (ಷರತ್ತು 12) — ಬಾಡಿಗೆದಾರರ ಒಪ್ಪಿಗೆಯಿಲ್ಲದೆ ಬಾಡಿಗೆ ಹೆಚ್ಚಿಸಲು ಅನುಮತಿ ನೀಡುತ್ತದೆ.\n\n**✅ ಶಿಫಾರಸು ಮಾಡಿದ ಕ್ರಮಗಳು**:\n• ಷರತ್ತು 7 ತೆಗೆದುಹಾಕಲು ಮಾತುಕತೆ ನಡೆಸಿ\n• ಕರ್ನಾಟಕ ಬಾಡಿಗೆ ನಿಯಂತ್ರಣ ಕಾಯ್ದೆ 2001 ರ ಪ್ರಕಾರ ಭದ್ರತಾ ಠೇವಣಿ ಮಿತಿಯನ್ನು ಒತ್ತಾಯಿಸಿ",
    default: "ಇದು ಒಂದು ಮುಖ್ಯ ಕಾನೂನು ಪ್ರಶ್ನೆ. ಭಾರತೀಯ ಕಾನೂನಿನ ಅಡಿ, ಉತ್ತರವು ನಿಮ್ಮ ನಿರ್ದಿಷ್ಟ ಸಂದರ್ಭಗಳು, ನ್ಯಾಯಾಧಿಕಾರ ಮತ್ತು ಅನ್ವಯವಾಗುವ ಕಾನೂನುಗಳನ್ನು ಒಳಗೊಂಡಂತೆ ಹಲವಾರು ಅಂಶಗಳನ್ನು ಅವಲಂಬಿಸಿದೆ. ವೈಯಕ್ತಿಕ ಸಲಹೆಗಾಗಿ ಅರ್ಹ ವಕೀಲರನ್ನು ಸಂಪರ್ಕಿಸಲು ನಾನು ಶಿಫಾರಸು ಮಾಡುತ್ತೇನೆ. ಈ ವಿಷಯದ ಯಾವುದೇ ನಿರ್ದಿಷ್ಟ ಅಂಶದ ಬಗ್ಗೆ ನೀವು ಹೆಚ್ಚಿನ ಮಾಹಿತಿ ಬಯಸುತ್ತೀರಾ?",
  },
};

// ─── Response Matching Logic ──────────────────────────────────────────────────
export function getAIResponse(query, lang) {
  const q = query.toLowerCase();
  const responses = MOCK_RESPONSES[lang];

  if (!responses) return MOCK_RESPONSES['en'].default;

  if (q.includes('tenant') || q.includes('rent') || q.includes('किराएदार') || q.includes('किराया') || q.includes('ಬಾಡಿಗೆ') || q.includes('ಕಿರಾಯ')) {
    return responses.tenantRights;
  }
  if (q.includes('consumer') || q.includes('complaint') || q.includes('उपभोक्ता') || q.includes('शिकायत') || q.includes('ಗ್ರಾಹಕ') || q.includes('ದೂರು')) {
    return responses.consumerComplaint;
  }
  if (q.includes('bail') || q.includes('anticipatory') || q.includes('जमानत') || q.includes('ಜಾಮೀನು') || q.includes('अग्रिम')) {
    return responses.bail;
  }
  if (q.includes('arrest') || q.includes('police') || q.includes('गिरफ्तार') || q.includes('पुलिस') || q.includes('ಬಂಧನ') || q.includes('ಪೊಲೀಸ್')) {
    return responses.arrest;
  }
  if (q.includes('property') || q.includes('land') || q.includes('संपत्ति') || q.includes('ಆಸ್ತಿ') || q.includes('भूमि')) {
    return responses.property;
  }

  return responses.default;
}
