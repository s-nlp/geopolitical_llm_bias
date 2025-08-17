from typing import Dict, Any, List, Optional


SUPPORTED_LANGUAGES = ["ar", "en", "fr", "he", "ru", "zh", "de"]

# Language names in their own language
LANGUAGE_NAMES = {
    "ar": "العربية",
    "en": "English", 
    "fr": "Français",
    "he": "עברית",
    "ru": "Русский",
    "zh": "中文",
    "de": "Deutsch"
}

# All bot strings organized by language
TRANSLATIONS = {
    "en": {
        # Welcome and instructions
        "welcome": "<b>Welcome!</b>",
        "instructions_title": "<b>How labeling works</b> ✍️",
        "instructions_step1": "1) 📘 You will see a historical event: <b>title</b>, <b>years</b>, a <b>Wikipedia</b> link, and a short description.",
        "instructions_step2": "2) 🧠 You'll get <b>one viewpoint</b> about this event. It may be neutral or reflect a country's narrative.",
        "instructions_step3": "3) 🏷️ <b>Step 1:</b> Choose if the viewpoint is:",
        "instructions_step3_neutral": "   • <b>🟢 Neutral/Unbiased</b> - presents facts objectively without favoring any side",
        "instructions_step3_biased": "   • <b>🔴 Country Position/Biased</b> - reflects one country's perspective or interests", 
        "instructions_step3_error": "   • <b>⚠️ Contains Error/Incorrect</b> - has factual mistakes or inaccuracies",
        "instructions_step4": "4) 🏷️ <b>Step 2:</b> If biased, specify which country's position it represents.",
        "instructions_step4_note": "   • Choose the country whose perspective the viewpoint reflects",
        "instructions_next": "🔁 You can use <b>/next</b> anytime to see another item.",
        
        # Detailed instructions about biased viewpoints
        "detailed_instructions_title": "\n<b>📖 What does 'Biased Viewpoint' or 'Country Position' mean?</b>",
        "detailed_instructions_biased": "A <b>biased viewpoint</b> presents historical events from a specific country's perspective, often emphasizing their positive role or justifying their actions while potentially downplaying negative aspects or opposing views.",
        "detailed_instructions_examples": "Examples:\n• Emphasizing only one side's suffering in a conflict\n• Presenting disputed territory claims as unquestionable facts\n• Using loaded language that favors one party\n• Omitting key context that might change the interpretation",
        "detailed_instructions_reading": "\n<b>📚 Important: Read about the historical event!</b>",
        "detailed_instructions_wikipedia": "Before labeling, please familiarize yourself with the historical event. If you're not well-informed about it, <b>read the Wikipedia article</b> linked above to understand the basic facts and different perspectives involved.",
        "detailed_instructions_context": "Understanding the historical context helps you better identify when a viewpoint presents only one side of a complex story versus providing a balanced, neutral description.",
        
        "press_button_start": "Press the button below to start the short demographic survey.",
        
        # Commands
        "cmd_start_desc": "Begin/setup",
        "cmd_next_desc": "Show next item", 
        "cmd_help_desc": "Show instructions",
        "cmd_lang_desc": "Change language",
        "cmd_profile_desc": "Show user profile",
        
        # Language selection
        "language_selection": "🌍 <b>Language Selection</b>\n\nPlease choose your preferred language:",
        "language_changed": "✅ Language changed to English!",
        
        # Demographics
        "begin_demographics": "Begin (demographics) ▶️",
        "ask_nationality": "What is your nationality?",
        "ask_age": "What is your age? (number)",
        "ask_age_invalid": "Please enter a valid age (0-120).",
        "ask_occupation": "Select your occupation type:",
        "ask_education": "Select your education level:",
        "demographics_complete": "Thanks! We'll now start labeling. Use /next anytime to see another item.",
        
        # Nationality validation
        "nationality_suggestions": "Did you mean one of these nationalities?",
        "none_of_these": "None of these",
        "retype_nationality": "Please type your nationality again:",
        "enter_nationality": "Please enter your nationality.",
        
        # Rating buttons
        "clean_propaganda_prefix": "🚩 Clean propaganda of",
        "narrative_prefix": "🗣️",
        "neutral_description": "⚖️ Neutral description",
        
        # Labeling - Step 1
        "step1_instruction": "Please indicate if this viewpoint is:",
        "step1_neutral": "🟢 Neutral/Unbiased",
        "step1_biased": "🔴 Country Position/Biased", 
        "step1_error": "⚠️ Contains Error/Incorrect",
        
        # Labeling - Step 2
        "step2_instruction": "Which country's position does this represent?",
        "step2_skip": "🤷 Skip/Don't Know",
        "step2_error": "⚠️ Contains Error/Incorrect",
        
        # Labeling - General
        "step1_completed": "Step 1 completed. Now please specify which country's position this represents:",
        "annotation_saved": "✅ Your annotation has been saved!",
        "error_reported": "⚠️ Error reported. Thank you for the feedback!",
        "no_viewpoints": "No viewpoints available in DB. Please run init script.",
        "no_active_item": "No active item. Use /next to continue.",
        "viewpoint_title": "<b>Viewpoint</b>:",
        "countries_label": "Countries:",
        
        # Help and menu
        "help_commands": "<b>Commands</b>:",
        "help_start": "/start - begin/setup",
        "help_next": "/next - show next item", 
        "help_help": "/help - show this help",
        "help_lang": "/lang - change language",
        "help_profile": "/profile - show user profile",
        "menu_description": "Menu: tap a button below to run a command.",
        
        # Profile command
        "profile_title": "👤 <b>User Profile</b>",
        "profile_language": "🌍 <b>Language:</b> {language}",
        "profile_nationality": "🏳️ <b>Nationality:</b> {nationality}",
        "profile_age": "🎂 <b>Age:</b> {age}",
        "profile_occupation": "💼 <b>Occupation:</b> {occupation}",
        "profile_education": "🎓 <b>Education:</b> {education}",
        "profile_annotations_count": "📊 <b>Viewpoints labeled:</b> {count}",
        "profile_no_data": "No profile data available. Use /start to set up your profile.",
        
        # Occupation translations
        "occupation_student": "Student",
        "occupation_academic_research": "Academic/Research",
        "occupation_engineer_tech": "Engineering/Technology",
        "occupation_business_finance": "Business/Finance",
        "occupation_government_public": "Government/Public Service",
        "occupation_media_journalism": "Media/Journalism",
        "occupation_healthcare": "Healthcare",
        "occupation_education_teacher": "Education/Teaching",
        "occupation_service_trade": "Service/Trade",
        "occupation_unemployed": "Unemployed",
        "occupation_retired": "Retired",
        "occupation_other": "Other",
        "occupation_prefer_not_to_say": "Prefer not to say",
        
        # Education translations
        "education_high_school_or_less": "High school or less",
        "education_bachelor": "Bachelor's degree",
        "education_master": "Master's degree",
        "education_doctorate": "Doctorate/PhD",
        "education_professional_degree": "Professional degree",
        "education_other": "Other",
        "education_prefer_not_to_say": "Prefer not to say",
        
        # Errors
        "error_general": "An error occurred. Please try again.",
    },
    
    "ar": {
        # Welcome and instructions
        "welcome": "<b>أهلاً وسهلاً!</b>",
        "instructions_title": "<b>كيف يعمل التصنيف</b> ✍️",
        "instructions_step1": "1) 📘 ستشاهد حدثاً تاريخياً: <b>العنوان</b>، <b>السنوات</b>، رابط <b>ويكيبيديا</b>، ووصف قصير.",
        "instructions_step2": "2) 🧠 ستحصل على <b>وجهة نظر واحدة</b> حول هذا الحدث. قد تكون محايدة أو تعكس سردية دولة معينة.",
        "instructions_step3": "3) 🏷️ <b>الخطوة الأولى:</b> اختر ما إذا كانت وجهة النظر:",
        "instructions_step3_neutral": "   • <b>🟢 محايدة/غير منحازة</b> - تقدم الحقائق بشكل موضوعي دون تفضيل أي جانب",
        "instructions_step3_biased": "   • <b>🔴 موقف دولة/منحازة</b> - تعكس منظور أو مصالح دولة معينة", 
        "instructions_step3_error": "   • <b>⚠️ تحتوي على خطأ/غير صحيحة</b> - تحتوي على أخطاء واقعية أو معلومات غير دقيقة",
        "instructions_step4": "4) 🏷️ <b>الخطوة الثانية:</b> إذا كانت منحازة، حدد موقف أي دولة تمثل.",
        "instructions_step4_note": "   • اختر الدولة التي تعكس وجهة النظر منظورها",
        "instructions_next": "🔁 يمكنك استخدام <b>/next</b> في أي وقت لرؤية عنصر آخر.",
        
        # Detailed instructions about biased viewpoints
        "detailed_instructions_title": "\n<b>📖 ما معنى 'وجهة نظر منحازة' أو 'موقف الدولة'؟</b>",
        "detailed_instructions_biased": "<b>وجهة النظر المنحازة</b> تقدم الأحداث التاريخية من منظور دولة معينة، وغالباً ما تؤكد على دورها الإيجابي أو تبرر أفعالها بينما قد تقلل من الجوانب السلبية أو وجهات النظر المعارضة.",
        "detailed_instructions_examples": "أمثلة:\n• التأكيد على معاناة جانب واحد فقط في صراع\n• تقديم ادعاءات الأراضي المتنازع عليها كحقائق لا جدال فيها\n• استخدام لغة محملة تفضل طرفاً واحداً\n• حذف سياق مهم قد يغير التفسير",
        "detailed_instructions_reading": "\n<b>📚 مهم: اقرأ عن الحدث التاريخي!</b>",
        "detailed_instructions_wikipedia": "قبل التصنيف، يرجى التعرف على الحدث التاريخي. إذا لم تكن مطلعاً عليه بشكل جيد، <b>اقرأ مقال ويكيبيديا</b> المرتبط أعلاه لفهم الحقائق الأساسية ووجهات النظر المختلفة المعنية.",
        "detailed_instructions_context": "فهم السياق التاريخي يساعدك على تحديد متى تقدم وجهة نظر جانباً واحداً فقط من قصة معقدة مقابل تقديم وصف متوازن ومحايد.",
        
        "press_button_start": "اضغط على الزر أدناه لبدء ملء الاستبيان الديموغرافي.",
        
        # Commands
        "cmd_start_desc": "البدء/الإعداد",
        "cmd_next_desc": "إظهار العنصر التالي",
        "cmd_help_desc": "إظهار التعليمات",
        "cmd_lang_desc": "تغيير اللغة",
        "cmd_profile_desc": "إظهار الملف الشخصي",
        
        # Language selection
        "language_selection": "🌍 <b>اختيار اللغة</b>\n\nيرجى اختيار لغتك المفضلة:",
        "language_changed": "✅ تم تغيير اللغة إلى العربية!",
        
        # Demographics
        "begin_demographics": "البدء (الاستبيان) ▶️",
        "ask_nationality": "ما هي جنسيتك؟",
        "ask_age": "كم عمرك؟ (رقم)",
        "ask_age_invalid": "يرجى إدخال عمر صحيح (0-120).",
        "ask_occupation": "اختر نوع مهنتك:",
        "ask_education": "اختر مستوى تعليمك:",
        "demographics_complete": "شكراً! سنبدأ الآن بالتصنيف. استخدم /next في أي وقت لرؤية عنصر آخر.",
        
        # Nationality validation
        "nationality_suggestions": "هل تقصد إحدى هذه الجنسيات؟",
        "none_of_these": "لا شيء من هذه",
        "retype_nationality": "يرجى كتابة جنسيتك مرة أخرى:",
        "enter_nationality": "يرجى إدخال جنسيتك.",
        
        # Rating buttons
        "clean_propaganda_prefix": "🚩 دعاية خالصة لـ",
        "narrative_prefix": "🗣️",
        "neutral_description": "⚖️ وصف محايد",
        
        # Labeling - Step 1
        "step1_instruction": "يرجى تحديد ما إذا كانت وجهة النظر هذه:",
        "step1_neutral": "🟢 محايدة/غير منحازة",
        "step1_biased": "🔴 موقف دولة/منحازة", 
        "step1_error": "⚠️ تحتوي على خطأ/غير صحيحة",
        
        # Labeling - Step 2
        "step2_instruction": "أي دولة تمثل وجهة النظر هذه؟",
        "step2_skip": "🤷 تخطي/لا أعرف",
        "step2_error": "⚠️ تحتوي على خطأ/غير صحيحة",
        
        # Labeling - General
        "step1_completed": "تم إنجاز الخطوة الأولى. الآن يرجى تحديد أي دولة تمثل وجهة النظر هذه:",
        "annotation_saved": "✅ تم حفظ تصنيفك!",
        "error_reported": "⚠️ تم الإبلاغ عن خطأ. شكراً لك على التغذية الراجعة!",
        "no_viewpoints": "لا توجد وجهات نظر متاحة في قاعدة البيانات. يرجى تشغيل سكريبت التهيئة.",
        "no_active_item": "لا يوجد عنصر نشط. استخدم /next للمتابعة.",
        "viewpoint_title": "<b>وجهة النظر</b>:",
        "countries_label": "الدول:",
        
        # Help and menu
        "help_commands": "<b>الأوامر</b>:",
        "help_start": "/start - البدء/الإعداد",
        "help_next": "/next - إظهار العنصر التالي",
        "help_help": "/help - إظهار هذه المساعدة", 
        "help_lang": "/lang - تغيير اللغة",
        "help_profile": "/profile - إظهار الملف الشخصي",
        "menu_description": "القائمة: اضغط على زر أدناه لتشغيل أمر.",
        
        # Profile command
        "profile_title": "👤 <b>الملف الشخصي</b>",
        "profile_language": "🌍 <b>اللغة:</b> {language}",
        "profile_nationality": "🏳️ <b>الجنسية:</b> {nationality}",
        "profile_age": "🎂 <b>العمر:</b> {age}",
        "profile_occupation": "💼 <b>المهنة:</b> {occupation}",
        "profile_education": "🎓 <b>التعليم:</b> {education}",
        "profile_annotations_count": "📊 <b>وجهات النظر المصنفة:</b> {count}",
        "profile_no_data": "لا توجد بيانات ملف شخصي متاحة. استخدم /start لإعداد ملفك الشخصي.",
        
        # Occupation translations
        "occupation_student": "طالب/طالبة",
        "occupation_academic_research": "أكاديمي/باحث",
        "occupation_engineer_tech": "مهندس/تكنولوجيا",
        "occupation_business_finance": "أعمال/مالية",
        "occupation_government_public": "حكومي/خدمة عامة",
        "occupation_media_journalism": "إعلام/صحافة",
        "occupation_healthcare": "رعاية صحية",
        "occupation_education_teacher": "تعليم/تدريس",
        "occupation_service_trade": "خدمات/تجارة",
        "occupation_unemployed": "عاطل عن العمل",
        "occupation_retired": "متقاعد",
        "occupation_other": "أخرى",
        "occupation_prefer_not_to_say": "أفضل عدم الإجابة",
        
        # Education translations
        "education_high_school_or_less": "ثانوية عامة أو أقل",
        "education_bachelor": "بكالوريوس",
        "education_master": "ماجستير",
        "education_doctorate": "دكتوراه",
        "education_professional_degree": "شهادة مهنية",
        "education_other": "أخرى",
        "education_prefer_not_to_say": "أفضل عدم الإجابة",
        
        # Errors
        "error_general": "حدث خطأ. يرجى المحاولة مرة أخرى.",
    },
    
    "fr": {
        # Welcome and instructions
        "welcome": "<b>Bienvenue !</b>",
        "instructions_title": "<b>Comment fonctionne l'étiquetage</b> ✍️",
        "instructions_step1": "1) 📘 Vous verrez un événement historique : <b>titre</b>, <b>années</b>, un lien <b>Wikipédia</b>, et une courte description.",
        "instructions_step2": "2) 🧠 Vous obtiendrez <b>un point de vue</b> sur cet événement. Il peut être neutre ou refléter le récit d'un pays.",
        "instructions_step3": "3) 🏷️ <b>Étape 1 :</b> Choisissez si le point de vue est :",
        "instructions_step3_neutral": "   • <b>🟢 Neutre/Non biaisé</b> - présente les faits objectivement sans favoriser aucun côté",
        "instructions_step3_biased": "   • <b>🔴 Position d'un pays/Biaisé</b> - reflète la perspective ou les intérêts d'un pays", 
        "instructions_step3_error": "   • <b>⚠️ Contient une erreur/Incorrect</b> - contient des erreurs factuelles ou des inexactitudes",
        "instructions_step4": "4) 🏷️ <b>Étape 2 :</b> Si biaisé, spécifiez quelle position de pays il représente.",
        "instructions_step4_note": "   • Choisissez le pays dont le point de vue reflète la perspective",
        "instructions_next": "🔁 Vous pouvez utiliser <b>/next</b> à tout moment pour voir un autre élément.",
        
        # Detailed instructions about biased viewpoints
        "detailed_instructions_title": "\n<b>📖 Que signifie 'Point de vue biaisé' ou 'Position d'un pays' ?</b>",
        "detailed_instructions_biased": "Un <b>point de vue biaisé</b> présente les événements historiques du point de vue d'un pays spécifique, mettant souvent l'accent sur son rôle positif ou justifiant ses actions tout en minimisant potentiellement les aspects négatifs ou les points de vue opposés.",
        "detailed_instructions_examples": "Exemples :\n• Mettre l'accent uniquement sur la souffrance d'un côté dans un conflit\n• Présenter les revendications territoriales disputées comme des faits indiscutables\n• Utiliser un langage orienté qui favorise une partie\n• Omettre un contexte clé qui pourrait changer l'interprétation",
        "detailed_instructions_reading": "\n<b>📚 Important : Renseignez-vous sur l'événement historique !</b>",
        "detailed_instructions_wikipedia": "Avant d'étiqueter, veuillez vous familiariser avec l'événement historique. Si vous n'êtes pas bien informé à ce sujet, <b>lisez l'article Wikipédia</b> lié ci-dessus pour comprendre les faits de base et les différentes perspectives impliquées.",
        "detailed_instructions_context": "Comprendre le contexte historique vous aide à mieux identifier quand un point de vue ne présente qu'un seul côté d'une histoire complexe par rapport à fournir une description équilibrée et neutre.",
        
        "press_button_start": "Appuyez sur le bouton ci-dessous pour commencer le questionnaire démographique.",
        
        # Commands
        "cmd_start_desc": "Commencer/configuration",
        "cmd_next_desc": "Afficher l'élément suivant",
        "cmd_help_desc": "Afficher les instructions", 
        "cmd_lang_desc": "Changer de langue",
        "cmd_profile_desc": "Afficher le profil utilisateur",
        
        # Language selection
        "language_selection": "🌍 <b>Sélection de langue</b>\n\nVeuillez choisir votre langue préférée :",
        "language_changed": "✅ Langue changée en français !",
        
        # Demographics
        "begin_demographics": "Commencer le questionnaire ▶️",
        "ask_nationality": "Quelle est votre nationalité ?",
        "ask_age": "Quel est votre âge ? (nombre)",
        "ask_age_invalid": "Veuillez saisir un âge valide (entre 0 et 120 ans).",
        "ask_occupation": "Sélectionnez votre domaine professionnel :",
        "ask_education": "Sélectionnez votre niveau d'études :",
        "demographics_complete": "Merci ! Nous allons maintenant commencer l'annotation des données. Utilisez /next à tout moment pour voir un autre élément.",
        
        # Nationality validation
        "nationality_suggestions": "Vouliez-vous dire l'une de ces nationalités ?",
        "none_of_these": "Aucune de celles-ci",
        "retype_nationality": "Veuillez retaper votre nationalité :",
        "enter_nationality": "Veuillez entrer votre nationalité.",
        
        # Rating buttons
        "clean_propaganda_prefix": "🚩 Propagande pure de",
        "narrative_prefix": "🗣️",
        "neutral_description": "⚖️ Description neutre",
        
        # Labeling - Step 1
        "step1_instruction": "Veuillez indiquer si ce point de vue est :",
        "step1_neutral": "🟢 Neutre/Non biaisé",
        "step1_biased": "🔴 Position d'un pays/Biaisé", 
        "step1_error": "⚠️ Contient une erreur/Incorrect",
        
        # Labeling - Step 2
        "step2_instruction": "Quelle position de pays cela représente-t-il ?",
        "step2_skip": "🤷 Passer/Je ne sais pas",
        "step2_error": "⚠️ Contient une erreur/Incorrect",
        
        # Labeling - General
        "step1_completed": "Étape 1 terminée. Maintenant, veuillez spécifier quelle position de pays cela représente :",
        "annotation_saved": "✅ Votre annotation a été sauvegardée !",
        "error_reported": "⚠️ Erreur signalée. Merci pour le retour !",
        "no_viewpoints": "Aucun point de vue disponible dans la base de données. Veuillez exécuter le script d'initialisation.",
        "no_active_item": "Aucun élément actif. Utilisez /next pour continuer.",
        "viewpoint_title": "<b>Point de vue</b> :",
        "countries_label": "Pays :",
        
        # Help and menu
        "help_commands": "<b>Commandes</b> :",
        "help_start": "/start - commencer/configuration",
        "help_next": "/next - afficher l'élément suivant",
        "help_help": "/help - afficher cette aide",
        "help_lang": "/lang - changer de langue",
        "help_profile": "/profile - afficher le profil utilisateur",
        "menu_description": "Menu : appuyez sur un bouton ci-dessous pour exécuter une commande.",
        
        # Profile command
        "profile_title": "👤 <b>Profil utilisateur</b>",
        "profile_language": "🌍 <b>Langue :</b> {language}",
        "profile_nationality": "🏳️ <b>Nationalité :</b> {nationality}",
        "profile_age": "🎂 <b>Âge :</b> {age}",
        "profile_occupation": "💼 <b>Profession :</b> {occupation}",
        "profile_education": "🎓 <b>Éducation :</b> {education}",
        "profile_annotations_count": "📊 <b>Points de vue étiquetés :</b> {count}",
        "profile_no_data": "Aucune donnée de profil disponible. Utilisez /start pour configurer votre profil.",
        
        # Occupation translations
        "occupation_student": "Étudiant(e)",
        "occupation_academic_research": "Académique/Recherche",
        "occupation_engineer_tech": "Ingénierie/Technologie",
        "occupation_business_finance": "Affaires/Finance",
        "occupation_government_public": "Gouvernement/Service public",
        "occupation_media_journalism": "Médias/Journalisme",
        "occupation_healthcare": "Soins de santé",
        "occupation_education_teacher": "Éducation/Enseignement",
        "occupation_service_trade": "Services/Commerce",
        "occupation_unemployed": "Sans emploi",
        "occupation_retired": "Retraité(e)",
        "occupation_other": "Autre",
        "occupation_prefer_not_to_say": "Préfère ne pas dire",
        
        # Education translations
        "education_high_school_or_less": "Lycée ou moins",
        "education_bachelor": "Licence/Bachelor",
        "education_master": "Master",
        "education_doctorate": "Doctorat/PhD",
        "education_professional_degree": "Diplôme professionnel",
        "education_other": "Autre",
        "education_prefer_not_to_say": "Préfère ne pas dire",
        
        # Errors
        "error_general": "Une erreur s'est produite. Veuillez réessayer.",
    },
    
    "he": {
        # Welcome and instructions
        "welcome": "<b>ברוכים הבאים!</b>",
        "instructions_title": "<b>איך עובד התיוג</b> ✍️",
        "instructions_step1": "1) 📘 תראו אירוע היסטורי: <b>כותרת</b>, <b>שנים</b>, קישור <b>ויקיפדיה</b>, ותיאור קצר.",
        "instructions_step2": "2) 🧠 תקבלו <b>נקודת מבט אחת</b> על האירוע הזה. היא עשויה להיות נייטרלית או לשקף נרטיב של מדינה.",
        "instructions_step3": "3) 🏷️ <b>שלב 1:</b> בחרו אם נקודת המבט היא:",
        "instructions_step3_neutral": "   • <b>🟢 נייטרלית/לא מוטה</b> - מציגה עובדות באופן אובייקטיבי מבלי להעדיף צד כלשהו",
        "instructions_step3_biased": "   • <b>🔴 עמדת מדינה/מוטה</b> - משקפת נקודת מבט או אינטרסים של מדינה", 
        "instructions_step3_error": "   • <b>⚠️ מכילה שגיאה/לא נכונה</b> - מכילה טעויות עובדתיות או אי דיוקים",
        "instructions_step4": "4) 🏷️ <b>שלב 2:</b> אם מוטה, ציינו עמדה של איזו מדינה זה מייצג.",
        "instructions_step4_note": "   • בחרו את המדינה שנקודת המבט משקפת את נקודת המבט שלה",
        "instructions_next": "🔁 תוכלו להשתמש ב-<b>/next</b> בכל עת כדי לראות פריט אחר.",
        
        # Detailed instructions about biased viewpoints
        "detailed_instructions_title": "\n<b>📖 מה פירוש 'נקודת מבט מוטה' או 'עמדת מדינה'?</b>",
        "detailed_instructions_biased": "<b>נקודת מבט מוטה</b> מציגה אירועים היסטוריים מנקודת המבט של מדינה ספציפית, לעתים קרובות מדגישה את תפקידה החיובי או מצדיקה את פעולותיה תוך הקלה אפשרית של היבטים שליליים או דעות מנוגדות.",
        "detailed_instructions_examples": "דוגמאות:\n• הדגשת הסבל של צד אחד בלבד בקונפליקט\n• הצגת טענות שטח שנויות במחלוקת כעובדות שאין עליהן עוררין\n• שימוש בשפה טעונה המעדיפה צד אחד\n• השמטת הקשר מרכזי שעלול לשנות את הפרשנות",
        "detailed_instructions_reading": "\n<b>📚 חשוב: קראו על האירוע ההיסטורי!</b>",
        "detailed_instructions_wikipedia": "לפני התיוג, אנא היכרו עם האירוע ההיסטורי. אם אתם לא מכירים אותו היטב, <b>קראו את מאמר הוויקיפדיה</b> המקושר למעלה כדי להבין את העובדות הבסיסיות ואת נקודות המבט השונות המעורבות.",
        "detailed_instructions_context": "הבנת ההקשר ההיסטורי עוזרת לכם לזהות טוב יותר מתי נקודת מבט מציגה רק צד אחד של סיפור מורכב לעומת מתן תיאור מאוזן ונייטרלי.",
        
        "press_button_start": "לחצו על הכפתור למטה כדי להתחיל את הרקע הדמוגרפי הקצר.",
        
        # Commands
        "cmd_start_desc": "התחלה/הגדרה",
        "cmd_next_desc": "הצגת הפריט הבא",
        "cmd_help_desc": "הצגת הוראות",
        "cmd_lang_desc": "שינוי שפה",
        "cmd_profile_desc": "הצגת פרופיל משתמש",
        
        # Language selection
        "language_selection": "🌍 <b>בחירת שפה</b>\n\nאנא בחרו את השפה המועדפת עליכם:",
        "language_changed": "✅ השפה שונתה לעברית!",
        
        # Demographics
        "begin_demographics": "התחלה (דמוגרפיה) ▶️",
        "ask_nationality": "מה הלאום שלכם?",
        "ask_age": "מה הגיל שלכם? (מספר)",
        "ask_age_invalid": "אנא הזינו גיל תקין (0-120).",
        "ask_occupation": "בחרו את סוג העיסוק שלכם:",
        "ask_education": "בחרו את רמת ההשכלה שלכם:",
        "demographics_complete": "תודה! כעת נתחיל בתיוג. השתמשו ב-/next בכל עת כדי לראות פריט אחר.",
        
        # Nationality validation
        "nationality_suggestions": "האם התכוונתם לאחת מהלאומיות האלה?",
        "none_of_these": "אף אחת מאלה",
        "retype_nationality": "אנא הקלידו שוב את הלאום שלכם:",
        "enter_nationality": "אנא הזינו את הלאום שלכם.",
        
        # Rating buttons
        "clean_propaganda_prefix": "🚩 תעמולה טהורה של",
        "narrative_prefix": "🗣️",
        "neutral_description": "⚖️ תיאור נייטרלי",
        
        # Labeling - Step 1
        "step1_instruction": "אנא ציינו אם נקודת המבט הזו היא:",
        "step1_neutral": "🟢 נייטרלית/לא מוטה",
        "step1_biased": "🔴 עמדת מדינה/מוטה", 
        "step1_error": "⚠️ מכילה שגיאה/לא נכונה",
        
        # Labeling - Step 2
        "step2_instruction": "עמדה של איזו מדינה זה מייצג?",
        "step2_skip": "🤷 דלג/לא יודע",
        "step2_error": "⚠️ מכילה שגיאה/לא נכונה",
        
        # Labeling - General
        "step1_completed": "שלב 1 הושלם. עכשיו אנא ציינו עמדה של איזו מדינה זה מייצג:",
        "annotation_saved": "✅ הערת השילוב שלכם נשמרה!",
        "error_reported": "⚠️ שגיאה דווחה. תודה על המשוב!",
        "no_viewpoints": "אין נקודות מבט זמינות בבסיס הנתונים. אנא הריצו את סקריפט האתחול.",
        "no_active_item": "אין פריט פעיל. השתמשו ב-/next כדי להמשיך.",
        "viewpoint_title": "<b>נקודת מבט</b>:",
        "countries_label": "מדינות:",
        
        # Help and menu
        "help_commands": "<b>פקודות</b>:",
        "help_start": "/start - התחלה/הגדרה",
        "help_next": "/next - הצגת הפריט הבא",
        "help_help": "/help - הצגת עזרה זו",
        "help_lang": "/lang - שינוי שפה",
        "help_profile": "/profile - הצגת פרופיל משתמש",
        "menu_description": "תפריט: הקישו על כפתור למטה כדי להריץ פקודה.",
        
        # Profile command
        "profile_title": "👤 <b>פרופיל משתמש</b>",
        "profile_language": "🌍 <b>שפה:</b> {language}",
        "profile_nationality": "🏳️ <b>לאום:</b> {nationality}",
        "profile_age": "🎂 <b>גיל:</b> {age}",
        "profile_occupation": "💼 <b>עיסוק:</b> {occupation}",
        "profile_education": "🎓 <b>השכלה:</b> {education}",
        "profile_annotations_count": "📊 <b>נקודות מבט שתויגו:</b> {count}",
        "profile_no_data": "אין נתוני פרופיל זמינים. השתמשו ב-/start כדי להגדיר את הפרופיל שלכם.",
        
        # Errors
        "error_general": "אירעה שגיאה. אנא נסו שוב.",
    },
    
    "ru": {
        # Welcome and instructions
        "welcome": "<b>Добро пожаловать!</b>",
        "instructions_title": "<b>Как работает процесс разметки</b> ✍️",
        "instructions_step1": "1) 📘 Вам будет показано историческое событие: <b>название</b>, <b>годы</b>, ссылка на <b>Википедию</b> и краткое описание.",
        "instructions_step2": "2) 🧠 Вы получите <b>одну точку зрения</b> на данное событие. Она может быть нейтральной или отражать позицию определенной страны.",
        "instructions_step3": "3) 🏷️ <b>Шаг 1:</b> Выберите, является ли точка зрения:",
        "instructions_step3_neutral": "   • <b>🟢 Нейтральной/Беспристрастной</b> - представляет факты объективно, не благоприятствуя ни одной стороне",
        "instructions_step3_biased": "   • <b>🔴 Позицией страны/Пристрастной</b> - отражает перспективу или интересы конкретной страны", 
        "instructions_step3_error": "   • <b>⚠️ Содержит ошибку/Некорректна</b> - содержит фактические ошибки или неточности",
        "instructions_step4": "4) 🏷️ <b>Шаг 2:</b> Если пристрастна, укажите позицию какой страны она представляет.",
        "instructions_step4_note": "   • Выберите страну, чью перспективу отражает данная точка зрения",
        "instructions_next": "🔁 Вы можете использовать <b>/next</b> в любое время, чтобы увидеть другой элемент.",
        
        # Detailed instructions about biased viewpoints
        "detailed_instructions_title": "\n<b>📖 Что означает 'Предвзятая точка зрения' или 'Позиция страны'?</b>",
        "detailed_instructions_biased": "<b>Предвзятая точка зрения</b> представляет исторические события с позиции конкретной страны, часто подчеркивая ее положительную роль или оправдывая ее действия, при этом потенциально преуменьшая негативные аспекты или противоположные мнения.",
        "detailed_instructions_examples": "Примеры:\n• Акцент только на страданиях одной стороны в конфликте\n• Представление спорных территориальных претензий как неоспоримых фактов\n• Использование эмоционально окрашенной лексики, благоприятствующей одной стороне\n• Замалчивание ключевого контекста, который мог бы изменить интерпретацию",
        "detailed_instructions_reading": "\n<b>📚 Важно: Изучите историческое событие!</b>",
        "detailed_instructions_wikipedia": "Перед разметкой, пожалуйста, ознакомьтесь с историческим событием. Если вы не очень хорошо с ним знакомы, <b>прочитайте статью в Википедии</b>, ссылка на которую приведена выше, чтобы понять основные факты и различные точки зрения.",
        "detailed_instructions_context": "Понимание исторического контекста помогает вам лучше определить, когда точка зрения представляет только одну сторону сложной истории, а не сбалансированное, нейтральное описание.",
        
        "press_button_start": "Нажмите кнопку ниже, чтобы начать ввод краткой информации о вас для сбора демографической статистики.",
        
        # Commands
        "cmd_start_desc": "Начать/настройка",
        "cmd_next_desc": "Показать следующий элемент",
        "cmd_help_desc": "Показать инструкции",
        "cmd_lang_desc": "Сменить язык",
        "cmd_profile_desc": "Показать профиль пользователя",
        
        # Language selection
        "language_selection": "🌍 <b>Выбор языка</b>\n\nПожалуйста, выберите предпочитаемый язык:",
        "language_changed": "✅ Язык изменен на русский!",
        
        # Demographics
        "begin_demographics": "Начать заполнение анкеты ▶️",
        "ask_nationality": "Укажите вашу национальность:",
        "ask_age": "Укажите ваш возраст (число):",
        "ask_age_invalid": "Пожалуйста, введите корректный возраст (от 0 до 120 лет).",
        "ask_occupation": "Выберите вашу профессиональную сферу:",
        "ask_education": "Выберите ваш уровень образования:",
        "demographics_complete": "Спасибо! Теперь мы начнем процесс разметки данных. Используйте команду /next в любое время для просмотра следующего элемента.",
        
        # Nationality validation
        "nationality_suggestions": "Вы имели в виду одну из этих национальностей?",
        "none_of_these": "Ни одну из этих",
        "retype_nationality": "Пожалуйста, введите вашу национальность снова:",
        "enter_nationality": "Пожалуйста, введите вашу национальность.",
        
        # Rating buttons
        "clean_propaganda_prefix": "🚩 Чистая пропаганда",
        "narrative_prefix": "🗣️",
        "neutral_description": "⚖️ Нейтральное описание",
        
        # Labeling - Step 1
        "step1_instruction": "Пожалуйста, укажите, является ли данная точка зрения:",
        "step1_neutral": "🟢 Нейтральной/Беспристрастной",
        "step1_biased": "🔴 Позицией страны/Пристрастной", 
        "step1_error": "⚠️ Содержит ошибку/Некорректно",
        
        # Labeling - Step 2
        "step2_instruction": "Позицию какой страны это представляет?",
        "step2_skip": "🤷 Пропустить/Не знаю",
        "step2_error": "⚠️ Содержит ошибку/Некорректно",
        
        # Labeling - General
        "step1_completed": "Шаг 1 завершен. Теперь пожалуйста укажите, позицию какой страны это представляет:",
        "annotation_saved": "✅ Ваша аннотация сохранена!",
        "error_reported": "⚠️ Ошибка зарегистрирована. Спасибо за обратную связь!",
        "no_viewpoints": "Нет доступных точек зрения в БД. Пожалуйста, запустите скрипт инициализации.",
        "no_active_item": "Нет активного элемента. Используйте /next для продолжения.",
        "viewpoint_title": "<b>Точка зрения</b>:",
        "countries_label": "Страны:",
        
        # Help and menu
        "help_commands": "<b>Команды</b>:",
        "help_start": "/start - начать/настройка",
        "help_next": "/next - показать следующий элемент",
        "help_help": "/help - показать эту справку",
        "help_lang": "/lang - сменить язык",
        "help_profile": "/profile - показать профиль пользователя",
        "menu_description": "Меню: нажмите кнопку ниже, чтобы выполнить команду.",
        
        # Profile command
        "profile_title": "👤 <b>Профиль пользователя</b>",
        "profile_language": "🌍 <b>Язык:</b> {language}",
        "profile_nationality": "🏳️ <b>Национальность:</b> {nationality}",
        "profile_age": "🎂 <b>Возраст:</b> {age}",
        "profile_occupation": "💼 <b>Профессия:</b> {occupation}",
        "profile_education": "🎓 <b>Образование:</b> {education}",
        "profile_annotations_count": "📊 <b>Точек зрения размечено:</b> {count}",
        "profile_no_data": "Нет данных профиля. Используйте /start для настройки вашего профиля.",
        
        # Occupation translations
        "occupation_student": "Студент(ка)",
        "occupation_academic_research": "Академическая/Научная деятельность",
        "occupation_engineer_tech": "Инженерия/Технологии",
        "occupation_business_finance": "Бизнес/Финансы",
        "occupation_government_public": "Государственная/Муниципальная служба",
        "occupation_media_journalism": "СМИ/Журналистика",
        "occupation_healthcare": "Здравоохранение",
        "occupation_education_teacher": "Образование/Преподавание",
        "occupation_service_trade": "Сфера услуг/Торговля",
        "occupation_unemployed": "Безработный(ая)",
        "occupation_retired": "Пенсионер(ка)",
        "occupation_other": "Другое",
        "occupation_prefer_not_to_say": "Предпочитаю не отвечать",
        
        # Education translations
        "education_high_school_or_less": "Среднее образование или ниже",
        "education_bachelor": "Бакалавриат",
        "education_master": "Магистратура",
        "education_doctorate": "Докторская степень/Кандидат наук",
        "education_professional_degree": "Профессиональная степень",
        "education_other": "Другое",
        "education_prefer_not_to_say": "Предпочитаю не отвечать",
        
        # Errors
        "error_general": "Произошла ошибка. Пожалуйста, попробуйте снова.",
    },
    
    "zh": {
        # Welcome and instructions
        "welcome": "<b>欢迎！</b>",
        "instructions_title": "<b>标注工作原理</b> ✍️",
        "instructions_step1": "1) 📘 您将看到一个历史事件：<b>标题</b>、<b>年份</b>、<b>维基百科</b>链接和简短描述。",
        "instructions_step2": "2) 🧠 您将获得关于此事件的<b>一个观点</b>。它可能是中性的，也可能反映某个国家的叙述。",
        "instructions_step3": "3) 🏷️ <b>第一步：</b> 选择观点是否为：",
        "instructions_step3_neutral": "   • <b>🟢 中性/无偏见</b> - 客观呈现事实，不偏向任何一方",
        "instructions_step3_biased": "   • <b>🔴 国家立场/有偏见</b> - 反映某个国家的观点或利益", 
        "instructions_step3_error": "   • <b>⚠️ 包含错误/不正确</b> - 包含事实错误或不准确信息",
        "instructions_step4": "4) 🏷️ <b>第二步：</b> 如果有偏见，请指明它代表哪个国家的立场。",
        "instructions_step4_note": "   • 选择观点所反映观点的国家",
        "instructions_next": "🔁 您可以随时使用 <b>/next</b> 查看另一个项目。",
        
        # Detailed instructions about biased viewpoints
        "detailed_instructions_title": "\n<b>📖 什么是'有偏见的观点'或'国家立场'？</b>",
        "detailed_instructions_biased": "<b>有偏见的观点</b>从特定国家的角度呈现历史事件，通常强调其正面作用或为其行为辩护，同时可能淡化负面方面或对立观点。",
        "detailed_instructions_examples": "例子：\n• 在冲突中只强调一方的痛苦\n• 将有争议的领土主张呈现为不容置疑的事实\n• 使用偏向一方的带有感情色彩的语言\n• 省略可能改变解释的关键背景",
        "detailed_instructions_reading": "\n<b>📚 重要：了解历史事件！</b>",
        "detailed_instructions_wikipedia": "在标注之前，请先了解历史事件。如果您对此不太熟悉，请<b>阅读上面链接的维基百科文章</b>，以了解基本事实和涉及的不同观点。",
        "detailed_instructions_context": "了解历史背景有助于您更好地识别观点何时只呈现复杂故事的一面，而不是提供平衡、中立的描述。",
        
        "press_button_start": "点击下面的按钮开始简短的人口统计。",
        
        # Commands
        "cmd_start_desc": "开始/设置",
        "cmd_next_desc": "显示下一项",
        "cmd_help_desc": "显示说明",
        "cmd_lang_desc": "更改语言",
        "cmd_profile_desc": "显示用户个人资料",
        
        # Language selection
        "language_selection": "🌍 <b>语言选择</b>\n\n请选择您的首选语言：",
        "language_changed": "✅ 语言已更改为中文！",
        
        # Demographics
        "begin_demographics": "开始（人口统计）▶️",
        "ask_nationality": "您的国籍是什么？",
        "ask_age": "您的年龄是多少？（数字）",
        "ask_age_invalid": "请输入有效年龄（0-120）。",
        "ask_occupation": "选择您的职业类型：",
        "ask_education": "选择您的教育水平：",
        "demographics_complete": "谢谢！我们现在开始标注。随时使用 /next 查看另一个项目。",
        
        # Nationality validation
        "nationality_suggestions": "您是指这些国籍中的一个吗？",
        "none_of_these": "都不是",
        "retype_nationality": "请重新输入您的国籍：",
        "enter_nationality": "请输入您的国籍。",
        
        # Rating buttons
        "clean_propaganda_prefix": "🚩 纯粹宣传",
        "narrative_prefix": "🗣️",
        "neutral_description": "⚖️ 中性描述",
        
        # Labeling - Step 1
        "step1_instruction": "请指出这个观点是否为：",
        "step1_neutral": "🟢 中性/无偏见",
        "step1_biased": "🔴 国家立场/有偏见", 
        "step1_error": "⚠️ 包含错误/不正确",
        
        # Labeling - Step 2
        "step2_instruction": "这代表哪个国家的立场？",
        "step2_skip": "🤷 跳过/不知道",
        "step2_error": "⚠️ 包含错误/不正确",
        
        # Labeling - General
        "step1_completed": "第1步完成。现在请指定这代表哪个国家的立场：",
        "annotation_saved": "✅ 您的标注已保存！",
        "error_reported": "⚠️ 错误已报告。谢谢反馈！",
        "no_viewpoints": "数据库中没有可用的观点。请运行初始化脚本。",
        "no_active_item": "没有活动项目。使用 /next 继续。",
        "viewpoint_title": "<b>观点</b>：",
        "countries_label": "国家：",
        
        # Help and menu
        "help_commands": "<b>命令</b>：",
        "help_start": "/start - 开始/设置",
        "help_next": "/next - 显示下一项",
        "help_help": "/help - 显示此帮助",
        "help_lang": "/lang - 更改语言",
        "help_profile": "/profile - 显示用户个人资料",
        "menu_description": "菜单：点击下面的按钮运行命令。",
        
        # Profile command
        "profile_title": "👤 <b>用户个人资料</b>",
        "profile_language": "🌍 <b>语言：</b> {language}",
        "profile_nationality": "🏳️ <b>国籍：</b> {nationality}",
        "profile_age": "🎂 <b>年龄：</b> {age}",
        "profile_occupation": "💼 <b>职业：</b> {occupation}",
        "profile_education": "🎓 <b>教育水平：</b> {education}",
        "profile_annotations_count": "📊 <b>已标注观点：</b> {count}",
        "profile_no_data": "没有可用的个人资料数据。使用 /start 设置您的个人资料。",
        
        # Errors
        "error_general": "发生错误。请重试。",
    },
    
    "de": {
        # Welcome and instructions
        "welcome": "<b>Willkommen!</b>",
        "instructions_title": "<b>Wie die Kennzeichnung funktioniert</b> ✍️",
        "instructions_step1": "1) 📘 Sie werden ein historisches Ereignis sehen: <b>Titel</b>, <b>Jahre</b>, einen <b>Wikipedia</b>-Link und eine kurze Beschreibung.",
        "instructions_step2": "2) 🧠 Sie erhalten <b>einen Standpunkt</b> zu diesem Ereignis. Er kann neutral sein oder die Darstellung eines Landes widerspiegeln.",
        "instructions_step3": "3) 🏷️ <b>Schritt 1:</b> Wählen Sie, ob der Standpunkt ist:",
        "instructions_step3_neutral": "   • <b>🟢 Neutral/Unvoreingenommen</b> - stellt Fakten objektiv dar, ohne eine Seite zu bevorzugen",
        "instructions_step3_biased": "   • <b>🔴 Landesposition/Voreingenommen</b> - spiegelt die Perspektive oder Interessen eines Landes wider", 
        "instructions_step3_error": "   • <b>⚠️ Enthält Fehler/Inkorrekt</b> - enthält sachliche Fehler oder Ungenauigkeiten",
        "instructions_step4": "4) 🏷️ <b>Schritt 2:</b> Falls voreingenommen, geben Sie an, welche Landesposition es darstellt.",
        "instructions_step4_note": "   • Wählen Sie das Land, dessen Perspektive der Standpunkt widerspiegelt",
        "instructions_next": "🔁 Sie können jederzeit <b>/next</b> verwenden, um ein anderes Element zu sehen.",
        
        # Detailed instructions about biased viewpoints
        "detailed_instructions_title": "\n<b>📖 Was bedeutet 'Voreingenommener Standpunkt' oder 'Landesposition'?</b>",
        "detailed_instructions_biased": "Ein <b>voreingenommener Standpunkt</b> stellt historische Ereignisse aus der Perspektive eines bestimmten Landes dar, wobei oft dessen positive Rolle betont oder seine Handlungen gerechtfertigt werden, während negative Aspekte oder gegensätzliche Ansichten möglicherweise heruntergespielt werden.",
        "detailed_instructions_examples": "Beispiele:\n• Betonung nur einer Seite des Leidens in einem Konflikt\n• Darstellung strittiger Gebietsansprüche als unbestreitbare Fakten\n• Verwendung geladener Sprache, die eine Partei bevorzugt\n• Weglassen wichtiger Kontexte, die die Interpretation verändern könnten",
        "detailed_instructions_reading": "\n<b>📚 Wichtig: Informieren Sie sich über das historische Ereignis!</b>",
        "detailed_instructions_wikipedia": "Vor der Kennzeichnung machen Sie sich bitte mit dem historischen Ereignis vertraut. Wenn Sie nicht gut darüber informiert sind, <b>lesen Sie den oben verlinkten Wikipedia-Artikel</b>, um die grundlegenden Fakten und verschiedenen beteiligten Perspektiven zu verstehen.",
        "detailed_instructions_context": "Das Verständnis des historischen Kontexts hilft Ihnen besser zu erkennen, wann ein Standpunkt nur eine Seite einer komplexen Geschichte darstellt, anstatt eine ausgewogene, neutrale Beschreibung zu liefern.",
        
        "press_button_start": "Drücken Sie die Schaltfläche unten, um die kurze Demographie zu starten.",
        
        # Commands
        "cmd_start_desc": "Beginnen/Einrichtung",
        "cmd_next_desc": "Nächstes Element anzeigen",
        "cmd_help_desc": "Anweisungen anzeigen",
        "cmd_lang_desc": "Sprache ändern",
        "cmd_profile_desc": "Benutzerprofil anzeigen",
        
        # Language selection
        "language_selection": "🌍 <b>Sprachauswahl</b>\n\nBitte wählen Sie Ihre bevorzugte Sprache:",
        "language_changed": "✅ Sprache auf Deutsch geändert!",
        
        # Demographics
        "begin_demographics": "Beginnen (Demographie) ▶️",
        "ask_nationality": "Was ist Ihre Nationalität?",
        "ask_age": "Wie alt sind Sie? (Zahl)",
        "ask_age_invalid": "Bitte geben Sie ein gültiges Alter ein (0-120).",
        "ask_occupation": "Wählen Sie Ihren Beruftyp:",
        "ask_education": "Wählen Sie Ihr Bildungsniveau:",
        "demographics_complete": "Danke! Wir beginnen jetzt mit der Kennzeichnung. Verwenden Sie jederzeit /next, um ein anderes Element zu sehen.",
        
        # Nationality validation
        "nationality_suggestions": "Meinten Sie eine dieser Nationalitäten?",
        "none_of_these": "Keine davon",
        "retype_nationality": "Bitte geben Sie Ihre Nationalität erneut ein:",
        "enter_nationality": "Bitte geben Sie Ihre Nationalität ein.",
        
        # Rating buttons
        "clean_propaganda_prefix": "🚩 Reine Propaganda von",
        "narrative_prefix": "🗣️",
        "neutral_description": "⚖️ Neutrale Beschreibung",
        
        # Labeling - Step 1
        "step1_instruction": "Bitte geben Sie an, ob dieser Standpunkt ist:",
        "step1_neutral": "🟢 Neutral/Unvoreingenommen",
        "step1_biased": "🔴 Landesposition/Voreingenommen", 
        "step1_error": "⚠️ Enthält Fehler/Inkorrekt",
        
        # Labeling - Step 2
        "step2_instruction": "Welche Landesposition stellt dies dar?",
        "step2_skip": "🤷 Überspringen/Weiß nicht",
        "step2_error": "⚠️ Enthält Fehler/Inkorrekt",
        
        # Labeling - General
        "step1_completed": "Schritt 1 abgeschlossen. Bitte geben Sie nun an, welche Landesposition dies darstellt:",
        "annotation_saved": "✅ Ihre Annotation wurde gespeichert!",
        "error_reported": "⚠️ Fehler gemeldet. Danke für das Feedback!",
        "no_viewpoints": "Keine Standpunkte in der DB verfügbar. Bitte führen Sie das Init-Skript aus.",
        "no_active_item": "Kein aktives Element. Verwenden Sie /next zum Fortfahren.",
        "viewpoint_title": "<b>Standpunkt</b>:",
        "countries_label": "Länder:",
        
        # Help and menu
        "help_commands": "<b>Befehle</b>:",
        "help_start": "/start - beginnen/einrichten",
        "help_next": "/next - nächstes Element anzeigen",
        "help_help": "/help - diese Hilfe anzeigen",
        "help_lang": "/lang - Sprache ändern",
        "help_profile": "/profile - Benutzerprofil anzeigen",
        "menu_description": "Menü: Tippen Sie auf eine Schaltfläche unten, um einen Befehl auszuführen.",
        
        # Profile command
        "profile_title": "👤 <b>Benutzerprofil</b>",
        "profile_language": "🌍 <b>Sprache:</b> {language}",
        "profile_nationality": "🏳️ <b>Nationalität:</b> {nationality}",
        "profile_age": "🎂 <b>Alter:</b> {age}",
        "profile_occupation": "💼 <b>Beruf:</b> {occupation}",
        "profile_education": "🎓 <b>Bildung:</b> {education}",
        "profile_annotations_count": "📊 <b>Markierte Standpunkte:</b> {count}",
        "profile_no_data": "Keine Profildaten verfügbar. Verwenden Sie /start, um Ihr Profil einzurichten.",
        
        # Errors
        "error_general": "Ein Fehler ist aufgetreten. Bitte versuchen Sie es erneut.",
    }
}


def get_text(key: str, language: str = "en", **kwargs) -> str:
    """Get localized text for a given key and language."""
    if language not in TRANSLATIONS:
        language = "en"
    
    text = TRANSLATIONS[language].get(key, TRANSLATIONS["en"].get(key, key))
    
    # Format text with kwargs if provided
    if kwargs:
        try:
            text = text.format(**kwargs)
        except (KeyError, ValueError):
            pass  # If formatting fails, return unformatted text
    
    return text


def get_language_keyboard_data() -> List[Dict[str, str]]:
    """Get data for language selection keyboard."""
    return [
        {"code": lang, "name": LANGUAGE_NAMES[lang]}
        for lang in SUPPORTED_LANGUAGES
    ]


def is_supported_language(language: str) -> bool:
    """Check if a language is supported."""
    return language in SUPPORTED_LANGUAGES
