/**
 * Language Templates Configuration
 * 
 * Default text templates for each supported language.
 * Custom text in profile overrides these defaults.
 * 
 * Fallback order: Custom → Default Template → English
 */

export const LANGUAGE_TEMPLATES = {
  english: {
    opening: {
      title: "Wedding Invitation",
      subtitle: "Join us in celebrating our special day"
    },
    welcome: {
      message: "With great joy, we invite you to witness the beginning of our journey together"
    },
    couple: {
      groomLabel: "Groom",
      brideLabel: "Bride"
    },
    events: {
      title: "Event Details",
      dateLabel: "Date",
      venueLabel: "Venue"
    },
    photos: {
      title: "Our Moments"
    },
    video: {
      title: "Our Story"
    },
    greetings: {
      title: "Wedding Wishes",
      nameLabel: "Your Name",
      messagePlaceholder: "Write your wishes here...",
      submitButton: "Send Wishes"
    },
    whatsapp: {
      groomButton: "Message Groom",
      brideButton: "Message Bride",
      defaultMessage: "Congratulations on your wedding! Wishing you both a lifetime of love and happiness."
    },
    footer: {
      thankyou: "Thank you for being part of our celebration"
    }
  },
  
  telugu: {
    opening: {
      title: "వివాహ ఆహ్వానం",
      subtitle: "మా ప్రత్యేక రోజును జరుపుకోవడానికి మాతో చేరండి"
    },
    welcome: {
      message: "చాలా సంతోషంతో, మా ప్రయాణ ప్రారంభానికి సాక్షిగా ఉండమని మిమ్మల్ని ఆహ్వానిస్తున్నాము"
    },
    couple: {
      groomLabel: "వరుడు",
      brideLabel: "వధువు"
    },
    events: {
      title: "కార్యక్రమ వివరాలు",
      dateLabel: "తేదీ",
      venueLabel: "స్థలం"
    },
    photos: {
      title: "మా జ్ఞాపకాలు"
    },
    video: {
      title: "మా కథ"
    },
    greetings: {
      title: "శుభాకాంక్షలు",
      nameLabel: "మీ పేరు",
      messagePlaceholder: "మీ శుభాకాంక్షలు ఇక్కడ రాయండి...",
      submitButton: "శుభాకాంక్షలు పంపండి"
    },
    whatsapp: {
      groomButton: "వరుడికి సందేశం పంపండి",
      brideButton: "వధువుకు సందేశం పంపండి",
      defaultMessage: "మీ వివాహానికి శుభాకాంక్షలు! మీ ఇద్దరికీ ప్రేమ మరియు సంతోషంతో నిండిన జీవితం కోరుకుంటున్నాను."
    },
    footer: {
      thankyou: "మా వేడుకలో భాగం అయినందుకు ధన్యవాదాలు"
    }
  },
  
  hindi: {
    opening: {
      title: "विवाह निमंत्रण",
      subtitle: "हमारे खास दिन को मनाने के लिए हमसे जुड़ें"
    },
    welcome: {
      message: "बहुत खुशी के साथ, हम आपको हमारी यात्रा की शुरुआत का गवाह बनने के लिए आमंत्रित करते हैं"
    },
    couple: {
      groomLabel: "वर",
      brideLabel: "वधू"
    },
    events: {
      title: "कार्यक्रम विवरण",
      dateLabel: "तारीख",
      venueLabel: "स्थान"
    },
    photos: {
      title: "हमारी यादें"
    },
    video: {
      title: "हमारी कहानी"
    },
    greetings: {
      title: "शुभकामनाएं",
      nameLabel: "आपका नाम",
      messagePlaceholder: "यहां अपनी शुभकामनाएं लिखें...",
      submitButton: "शुभकामनाएं भेजें"
    },
    whatsapp: {
      groomButton: "वर को संदेश भेजें",
      brideButton: "वधू को संदेश भेजें",
      defaultMessage: "आपकी शादी की बधाई! आप दोनों को प्यार और खुशियों से भरी जिंदगी की शुभकामनाएं।"
    },
    footer: {
      thankyou: "हमारे उत्सव का हिस्सा बनने के लिए धन्यवाद"
    }
  }
};

/**
 * Language metadata
 */
export const LANGUAGES = [
  {
    code: 'english',
    name: 'English',
    nativeName: 'English',
    rtl: false
  },
  {
    code: 'telugu',
    name: 'Telugu',
    nativeName: 'తెలుగు',
    rtl: false
  },
  {
    code: 'hindi',
    name: 'Hindi',
    nativeName: 'हिन्दी',
    rtl: false
  }
];

/**
 * Get text for a specific section and language
 * @param {string} language - Language code
 * @param {string} section - Section name
 * @param {string} key - Text key
 * @param {object} customText - Custom text overrides from profile
 * @returns {string} Text content with fallback
 */
export const getText = (language, section, key, customText = {}) => {
  // Check custom text first
  if (customText[language] && customText[language][`${section}_${key}`]) {
    return customText[language][`${section}_${key}`];
  }
  
  // Check language template
  if (LANGUAGE_TEMPLATES[language] && 
      LANGUAGE_TEMPLATES[language][section] && 
      LANGUAGE_TEMPLATES[language][section][key]) {
    return LANGUAGE_TEMPLATES[language][section][key];
  }
  
  // Fallback to English
  if (LANGUAGE_TEMPLATES.english[section] && 
      LANGUAGE_TEMPLATES.english[section][key]) {
    return LANGUAGE_TEMPLATES.english[section][key];
  }
  
  return '';
};

/**
 * Get all text for a section in a language
 * @param {string} language - Language code
 * @param {string} section - Section name
 * @param {object} customText - Custom text overrides from profile
 * @returns {object} Section text with fallback
 */
export const getSectionText = (language, section, customText = {}) => {
  const template = LANGUAGE_TEMPLATES[language]?.[section] || LANGUAGE_TEMPLATES.english[section];
  
  if (!template) return {};
  
  const result = { ...template };
  
  // Apply custom overrides
  if (customText[language]) {
    Object.keys(result).forEach(key => {
      const customKey = `${section}_${key}`;
      if (customText[language][customKey]) {
        result[key] = customText[language][customKey];
      }
    });
  }
  
  return result;
};

/**
 * Get language metadata by code
 * @param {string} code - Language code
 * @returns {object|null} Language metadata
 */
export const getLanguage = (code) => {
  return LANGUAGES.find(lang => lang.code === code);
};
