/**
 * Multi-Language Translation System
 * Supports: English (en), Kannada (kn), Telugu (te), Hindi (hi)
 * Uses client-side dictionary and localStorage persistence.
 */

(function () {
  const LANG_KEY = 'expense_split_language';
  const DEFAULT_LANG = 'en';

  const translations = {
    en: {
      // Navigation
      nav_dashboard: "Dashboard",
      nav_groups: "Groups",
      nav_expenses: "Expenses",
      nav_balances: "Balances",
      nav_budgets: "Budgets",
      nav_simulator: "Simulator",
      nav_login: "Login",
      nav_register: "Register",
      nav_logout: "Logout",

      // Dashboard
      dash_title: "Financial Overview",
      dash_subtitle: "Track your shared spending, group balances, and budget health",
      dash_total_expenses: "Total Group Expenses",
      dash_total_paid: "Total Amount You Paid",
      dash_you_owe: "You Owe",
      dash_owed_to_you: "You Are Owed",
      dash_groups_count: "Active Groups",
      dash_recent_expenses: "Recent Transactions",
      dash_monthly_trend: "Monthly Spending Trend",
      dash_category_breakdown: "Expense Category Breakdown",
      dash_group_comparison: "Group-wise Spending",
      dash_budget_usage: "Group Budget Usage",
      dash_budget_alerts: "Budget Health & Alerts",

      // Quick Actions
      action_create_group: "Create Group",
      action_add_expense: "Add Expense",
      action_view_groups: "View Groups",
      action_view_balances: "View Balances",
      action_simulate: "Run Simulator",
      action_confirm_add: "Confirm & Add Expense",
      action_save: "Save",
      action_cancel: "Cancel",
      action_edit: "Edit",
      action_delete: "Delete",

      // Form labels
      label_name: "Full Name",
      label_email: "Email Address",
      label_password: "Password",
      label_confirm_password: "Confirm Password",
      label_group_name: "Group Name",
      label_description: "Description",
      label_monthly_budget: "Monthly Budget (₹)",
      label_amount: "Amount (₹)",
      label_category: "Category",
      label_date: "Date",
      label_paid_by: "Paid By",
      label_split_method: "Split Method",
      label_participants: "Participants Sharing This Expense",

      // Split Methods
      split_equal: "Equal Split",
      split_percentage: "Percentage Split",
      split_custom: "Custom Split",

      // Categories
      cat_food: "Food & Dining",
      cat_transport: "Transportation",
      cat_shopping: "Shopping",
      cat_utilities: "Utilities & Bills",
      cat_entertainment: "Entertainment",
      cat_housing: "Housing & Rent",
      cat_healthcare: "Healthcare",
      cat_groceries: "Groceries",
      cat_travel: "Travel",
      cat_other: "Other",

      // Balances & Status
      status_gets_back: "Gets Back",
      status_owes: "Owes",
      status_settled: "Settled",
      who_owes_whom: "Who Owes Whom (Settlements)",
      no_expenses: "No expenses recorded yet.",
      no_groups: "You are not a member of any group yet.",

      // Budget Warnings
      budget_normal: "Normal (< 75%)",
      budget_warning: "Warning (75% - 90%)",
      budget_high_alert: "High Alert (90% - 100%)",
      budget_exceeded: "Budget Exceeded (100%+)"
    },

    kn: {
      // Navigation (Kannada)
      nav_dashboard: "ಡ್ಯಾಶ್‌ಬೋರ್ಡ್",
      nav_groups: "ಗುಂಪುಗಳು",
      nav_expenses: "ಖರ್ಚುಗಳು",
      nav_balances: "ಬಾಕಿ ಮೊತ್ತ",
      nav_budgets: "ಬಜೆಟ್‌ಗಳು",
      nav_simulator: "ಸಿಮ್ಯುಲೇಟರ್",
      nav_login: "ಲಾಗಿನ್",
      nav_register: "ನೋಂದಣಿ",
      nav_logout: "ಲಾಗ್ ಔಟ್",

      // Dashboard
      dash_title: "ಆರ್ಥಿಕ ಅವಲೋಕನ",
      dash_subtitle: "ಹಂಚಿಕೆಯಾದ ಖರ್ಚು, ಬಾಕಿ ಮತ್ತು ಬಜೆಟ್ ಪರಿಶೀಲಿಸಿ",
      dash_total_expenses: "ಒಟ್ಟು ಗುಂಪಿನ ಖರ್ಚು",
      dash_total_paid: "ನೀವು ಪಾವತಿಸಿದ ಒಟ್ಟು ಹಣ",
      dash_you_owe: "ನೀವು ನೀಡಬೇಕಾದದ್ದು",
      dash_owed_to_you: "ನಿಮಗೆ ಬರಬೇಕಾದದ್ದು",
      dash_groups_count: "ಸಕ್ರಿಯ ಗುಂಪುಗಳು",
      dash_recent_expenses: "ಇತ್ತೀಚಿನ ವಹಿವಾಟುಗಳು",
      dash_monthly_trend: "ಮಾಸಿಕ ಖರ್ಚಿನ ಪ್ರವೃತ್ತಿ",
      dash_category_breakdown: "ವರ್ಗವಾರು ಖರ್ಚಿನ ವಿಭಾಗ",
      dash_group_comparison: "ಗುಂಪುವಾರು ಖರ್ಚಿನ ಹೋಲಿಕೆ",
      dash_budget_usage: "ಬಜೆಟ್ ಬಳಕೆ ವಿವರ",
      dash_budget_alerts: "ಬಜೆಟ್ ಎಚ್ಚರಿಕೆಗಳು",

      // Quick Actions
      action_create_group: "ಹೊಸ ಗುಂಪು ರಚಿಸಿ",
      action_add_expense: "ಖರ್ಚು ಸೇರಿಸಿ",
      action_view_groups: "ಗುಂಪುಗಳನ್ನು ನೋಡಿ",
      action_view_balances: "ಬಾಕಿಗಳನ್ನು ನೋಡಿ",
      action_simulate: "ಸಿಮ್ಯುಲೇಶನ್ ಮಾಡಿ",
      action_confirm_add: "ಖಚಿತಪಡಿಸಿ ಖರ್ಚು ಸೇರಿಸಿ",
      action_save: "ಉಳಿಸಿ",
      action_cancel: "ರದ್ದುಮಾಡಿ",
      action_edit: "ತಿದ್ದುಪಡಿ",
      action_delete: "ಅಳಿಸಿ",

      // Form labels
      label_name: "ಪೂರ್ಣ ಹೆಸರು",
      label_email: "ಇಮೇಲ್ ವಿಳಾಸ",
      label_password: "ಪಾಸ್‌ವರ್ಡ್",
      label_confirm_password: "ಪಾಸ್‌ವರ್ಡ್ ದೃಢೀಕರಿಸಿ",
      label_group_name: "ಗುಂಪಿನ ಹೆಸರು",
      label_description: "ವಿವರಣೆ",
      label_monthly_budget: "ಮಾಸಿಕ ಬಜೆಟ್ (₹)",
      label_amount: "ಮೊತ್ತ (₹)",
      label_category: "ವರ್ಗ",
      label_date: "ದಿನಾಂಕ",
      label_paid_by: "ಪಾವತಿಸಿದವರು",
      label_split_method: "ಹಂಚಿಕೆ ವಿಧಾನ",
      label_participants: "ಹಂಚಿಕೊಳ್ಳುವ ಸದಸ್ಯರು",

      // Split Methods
      split_equal: "ಸಮಾನ ಹಂಚಿಕೆ",
      split_percentage: "ಶೇಕಡಾವಾರು ಹಂಚಿಕೆ",
      split_custom: "ಕಸ್ಟಮ್ ಹಂಚಿಕೆ",

      // Categories
      cat_food: "ಆಹಾರ ಮತ್ತು ಊಟ",
      cat_transport: "ಸಾರಿಗೆ",
      cat_shopping: "ಖರೀದಿ",
      cat_utilities: "ಯುಟಿಲಿಟಿ ಮತ್ತು ಬಿಲ್‌ಗಳು",
      cat_entertainment: "ಮನರಂಜನೆ",
      cat_housing: "ಮನೆ ಬಾಡಿಗೆ",
      cat_healthcare: "ಆರೋಗ್ಯ",
      cat_groceries: "ದಿನಸಿ",
      cat_travel: "ಪ್ರವಾಸ",
      cat_other: "ಇತರ",

      // Balances & Status
      status_gets_back: "ಮರಳಿ ಬರಲಿದೆ",
      status_owes: "ನೀಡಬೇಕಿದೆ",
      status_settled: "ಪೂರ್ಣಗೊಂಡಿದೆ",
      who_owes_whom: "ಯಾರು ಯಾರಿಗೆ ನೀಡಬೇಕು",
      no_expenses: "ಇನ್ನೂ ಯಾವುದೇ ಖರ್ಚು ದಾಖಲಾಗಿಲ್ಲ.",
      no_groups: "ನೀವು ಯಾವುದೇ ಗುಂಪಿನಲ್ಲಿ ಇಲ್ಲ.",

      // Budget Warnings
      budget_normal: "ಸಾಮಾನ್ಯ (< 75%)",
      budget_warning: "ಎಚ್ಚರಿಕೆ (75% - 90%)",
      budget_high_alert: "ಹೆಚ್ಚಿನ ಖರ್ಚಿನ ಎಚ್ಚರಿಕೆ (90% - 100%)",
      budget_exceeded: "ಬಜೆಟ್ ಮೀರಿದೆ (100%+)"
    },

    te: {
      // Navigation (Telugu)
      nav_dashboard: "డ్యాష్‌బోర్డ్",
      nav_groups: "గ్రూపులు",
      nav_expenses: "ఖర్చులు",
      nav_balances: "బ్యాలెన్స్‌లు",
      nav_budgets: "బడ్జెట్‌లు",
      nav_simulator: "సిమ్యులేటర్",
      nav_login: "లాగిన్",
      nav_register: "నమోదు",
      nav_logout: "లాగ్ అవుట్",

      // Dashboard
      dash_title: "ఆర్థిక వివరణ",
      dash_subtitle: "మీ ఉమ్మడి ఖర్చులు, సమూహ బ్యాలెన్స్‌లు మరియు బడ్జెట్ ట్రాక్ చేయండి",
      dash_total_expenses: "మొత్తం గ్రూప్ ఖర్చులు",
      dash_total_paid: "మీరు చెల్లించిన మొత్తం",
      dash_you_owe: "మీరు ఇవ్వాల్సినవి",
      dash_owed_to_you: "మీకు రావాల్సినవి",
      dash_groups_count: "యాక్టివ్ గ్రూపులు",
      dash_recent_expenses: "ఇటీవలి లావాదేవీలు",
      dash_monthly_trend: "నెలవారీ ఖర్చుల సరళి",
      dash_category_breakdown: "కేటగిరీ వారీ ఖర్చులు",
      dash_group_comparison: "గ్రూపుల వారీ ఖర్చుల పోలిక",
      dash_budget_usage: "బడ్జెట్ వినియోగం",
      dash_budget_alerts: "బడ్జెట్ హెచ్చరికలు",

      // Quick Actions
      action_create_group: "గ్రూప్ సృష్టించండి",
      action_add_expense: "ఖర్చు జోడించండి",
      action_view_groups: "గ్రూపులను చూడండి",
      action_view_balances: "బ్యాలెన్స్‌లు చూడండి",
      action_simulate: "సిమ్యులేషన్ చేయండి",
      action_confirm_add: "నిర్ధారించి ఖర్చు చేర్చండి",
      action_save: "సేవ్ చేయండి",
      action_cancel: "రద్దు చేయండి",
      action_edit: "సవరించు",
      action_delete: "తొలగించు",

      // Form labels
      label_name: "పూర్తి పేరు",
      label_email: "ఈమెయిల్ చిరునామా",
      label_password: "పాస్‌వర్డ్",
      label_confirm_password: "పాస్‌వర్డ్ నిర్ధారించండి",
      label_group_name: "గ్రూప్ పేరు",
      label_description: "వివరణ",
      label_monthly_budget: "నెలవారీ బడ్జెట్ (₹)",
      label_amount: "మొత్తం (₹)",
      label_category: "కేటగిరీ",
      label_date: "తేదీ",
      label_paid_by: "చెల్లించిన వారు",
      label_split_method: "విభజన పద్ధతి",
      label_participants: "భాగస్వామ్య సభ్యులు",

      // Split Methods
      split_equal: "సమాన విభజన",
      split_percentage: "శాతం విభజన",
      split_custom: "కస్టమ్ విభజన",

      // Categories
      cat_food: "ఆహారం & భోజనం",
      cat_transport: "రవాణా",
      cat_shopping: "షాపింగ్",
      cat_utilities: "యుటిలిటీస్ & బిల్లులు",
      cat_entertainment: "వినోదం",
      cat_housing: "ఇంటి అద్దె",
      cat_healthcare: "వైద్యం",
      cat_groceries: "కిరాణా",
      cat_travel: "ప్రయాణం",
      cat_other: "ఇతర",

      // Balances & Status
      status_gets_back: "తిరిగి రావలసినది",
      status_owes: "ఇవ్వవలసినది",
      status_settled: "సెటిల్ చేయబడింది",
      who_owes_whom: "ఎవరు ఎవరికి ఇవ్వాలి",
      no_expenses: "ఇంకా ఖర్చులు నమోదు కాలేదు.",
      no_groups: "మీరు ఏ గ్రూప్‌లోనూ లేరు.",

      // Budget Warnings
      budget_normal: "సాధారణం (< 75%)",
      budget_warning: "హెచ్చరిక (75% - 90%)",
      budget_high_alert: "అధిక ఖర్చు హెచ్చరిక (90% - 100%)",
      budget_exceeded: "బడ్జెట్ దాటిపోయింది (100%+)"
    },

    hi: {
      // Navigation (Hindi)
      nav_dashboard: "डैशबोर्ड",
      nav_groups: "समूह",
      nav_expenses: "खर्च",
      nav_balances: "बकाया राशि",
      nav_budgets: "बजट",
      nav_simulator: "सिम्युलेटर",
      nav_login: "लॉग इन",
      nav_register: "पंजीकरण",
      nav_logout: "लॉग आउट",

      // Dashboard
      dash_title: "वित्तीय अवलोकन",
      dash_subtitle: "साझा खर्च, समूह बकाया और बजट स्थिति ट्रैक करें",
      dash_total_expenses: "कुल समूह खर्च",
      dash_total_paid: "आपके द्वारा भुगतान किया गया",
      dash_you_owe: "आपको देना है",
      dash_owed_to_you: "आपको मिलना है",
      dash_groups_count: "सक्रिय समूह",
      dash_recent_expenses: "हाल के लेन-देन",
      dash_monthly_trend: "मासिक खर्च का रुझान",
      dash_category_breakdown: "श्रेणी अनुसार खर्च",
      dash_group_comparison: "समूहवार खर्च तुलना",
      dash_budget_usage: "बजट उपयोग विवरण",
      dash_budget_alerts: "बजट स्वास्थ्य और अलर्ट",

      // Quick Actions
      action_create_group: "समूह बनाएं",
      action_add_expense: "खर्च जोड़ें",
      action_view_groups: "समूह देखें",
      action_view_balances: "बकाया देखें",
      action_simulate: "सिम्युलेशन चलाएं",
      action_confirm_add: "पुष्टि करें और खर्च जोड़ें",
      action_save: "सहेजें",
      action_cancel: "रद्द करें",
      action_edit: "संपादित करें",
      action_delete: "हटाएं",

      // Form labels
      label_name: "पूरा नाम",
      label_email: "ईमेल पता",
      label_password: "पासवर्ड",
      label_confirm_password: "पासवर्ड की पुष्टि करें",
      label_group_name: "समूह का नाम",
      label_description: "विवरण",
      label_monthly_budget: "मासिक बजट (₹)",
      label_amount: "राशि (₹)",
      label_category: "श्रेणी",
      label_date: "तारीख",
      label_paid_by: "भुगतानकर्ता",
      label_split_method: "विभाजन का तरीका",
      label_participants: "साझेदार सदस्य",

      // Split Methods
      split_equal: "बराबर विभाजन",
      split_percentage: "प्रतिशत विभाजन",
      split_custom: "कस्टम विभाजन",

      // Categories
      cat_food: "भोजन और रेस्टोरेंट",
      cat_transport: "परिवहन",
      cat_shopping: "खरीदारी",
      cat_utilities: "उपयोगिता और बिल",
      cat_entertainment: "मनोरंजन",
      cat_housing: "मकान किराया",
      cat_healthcare: "स्वास्थ्य देखभाल",
      cat_groceries: "किराना",
      cat_travel: "यात्रा",
      cat_other: "अन्य",

      // Balances & Status
      status_gets_back: "वापस मिलेगा",
      status_owes: "देना होगा",
      status_settled: "निपटारा हुआ",
      who_owes_whom: "किसे किसे भुगतान करना है",
      no_expenses: "अभी तक कोई खर्च दर्ज नहीं किया गया है।",
      no_groups: "आप अभी किसी समूह के सदस्य नहीं हैं।",

      // Budget Warnings
      budget_normal: "सामान्य (< 75%)",
      budget_warning: "चेतावनी (75% - 90%)",
      budget_high_alert: "उच्च खर्च अलर्ट (90% - 100%)",
      budget_exceeded: "बजट समाप्त/पार (100%+)"
    }
  };

  function getSavedLanguage() {
    return localStorage.getItem(LANG_KEY) || DEFAULT_LANG;
  }

  function applyLanguage(lang) {
    if (!translations[lang]) {
      lang = DEFAULT_LANG;
    }

    const dict = translations[lang];

    // Update all elements with data-i18n attribute
    document.querySelectorAll('[data-i18n]').forEach(el => {
      const key = el.getAttribute('data-i18n');
      if (dict[key]) {
        el.textContent = dict[key];
      }
    });

    // Update placeholders with data-i18n-placeholder
    document.querySelectorAll('[data-i18n-placeholder]').forEach(el => {
      const key = el.getAttribute('data-i18n-placeholder');
      if (dict[key]) {
        el.setAttribute('placeholder', dict[key]);
      }
    });

    // Update selector dropdown if present
    const langSelect = document.getElementById('language-select');
    if (langSelect && langSelect.value !== lang) {
      langSelect.value = lang;
    }

    localStorage.setItem(LANG_KEY, lang);
    document.documentElement.lang = lang;
  }

  document.addEventListener('DOMContentLoaded', function () {
    const savedLang = getSavedLanguage();
    applyLanguage(savedLang);

    const langSelect = document.getElementById('language-select');
    if (langSelect) {
      langSelect.value = savedLang;
      langSelect.addEventListener('change', function () {
        applyLanguage(this.value);
      });
    }
  });

  window.LanguageManager = {
    getLanguage: getSavedLanguage,
    setLanguage: applyLanguage,
    t: function (key) {
      const lang = getSavedLanguage();
      return (translations[lang] && translations[lang][key]) || (translations['en'][key]) || key;
    }
  };
})();
