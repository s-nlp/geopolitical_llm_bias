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
        "welcome_acknowledgment": "🎓 <b>Special Recognition:</b> Users who label 50 viewpoints will be acknowledged in our research paper!",
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
        "detailed_instructions_misinformation": "\n<b>🔍 Important distinction: Misinformation vs. Errors</b>\nIf a viewpoint contains misinformation that appears to be used for manipulation or to advance a particular narrative, classify it as <b>biased</b> rather than an error. Only mark something as an 'error' if it contains clear factual mistakes without apparent manipulative intent.",
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
        "step1_neutral": "🟢 ✅ Neutral/Unbiased",
        "step1_biased": "🔴 ⚖️ Country Position/Biased", 
        "step1_error": "⚠️ ❌ Contains Error/Incorrect",
        
        # Labeling - Step 2
        "step2_instruction": "Which country's position does this represent?",
        "step2_skip": "🤷 ❓ Skip/Don't Know",
        "step2_error": "⚠️ ❌ Contains Error/Incorrect",
        
        # Labeling - General
        "step1_completed": "Step 1 completed. Now please specify which country's position this represents:",
        "annotation_saved": "✅ Your annotation has been saved!",
        "milestone_10": "🎉 Congratulations! You've labeled 10 viewpoints! You're doing great work!",
        "milestone_25": "🌟 Amazing! You've reached 25 viewpoints! Your contribution is really valuable!",
        "milestone_40": "🏆 Outstanding! 40 viewpoints labeled! You're making a significant impact on our research!",
        
        # Event grouping
        "event_group_info": "📚 <b>Event Group:</b> This event has {total} viewpoints. You're on viewpoint {current} of {total}.",
        "next_viewpoint": "➡️ Next Viewpoint",
        "previous_viewpoint": "⬅️ Previous Viewpoint", 
        "finish_event": "✅ Finish Event",
        "event_complete": "🎉 You've completed all viewpoints for this event! Great job!",
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
        
        # Registration
        "registration_required": "⚠️ <b>Registration Required</b>\n\nYou need to complete registration before using the bot. Please use /start to begin the registration process.",
        
        # Errors
        "error_general": "An error occurred. Please try again.",
    },
    
    "ar": {
        # Welcome and instructions
        "welcome": "<b>أهلاً وسهلاً!</b>",
        "welcome_acknowledgment": "🎓 <b>اعتراف خاص:</b> المستخدمون الذين يصنفون 50 وجهة نظر سيتم ذكرهم في ورقتنا البحثية!",
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
        "detailed_instructions_misinformation": "\n<b>🔍 تمييز مهم: المعلومات المضللة مقابل الأخطاء</b>\nإذا كانت وجهة النظر تحتوي على معلومات مضللة يبدو أنها تُستخدم للتلاعب أو لتعزيز سردية معينة، صنفها كـ<b>منحازة</b> وليس كخطأ. قم بتمييز شيء كـ'خطأ' فقط إذا كان يحتوي على أخطاء واقعية واضحة دون نية تلاعبية واضحة.",
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
        "step1_neutral": "🟢 ✅ محايدة/غير منحازة",
        "step1_biased": "🔴 ⚖️ موقف دولة/منحازة", 
        "step1_error": "⚠️ ❌ تحتوي على خطأ/غير صحيحة",
        
        # Labeling - Step 2
        "step2_instruction": "أي دولة تمثل وجهة النظر هذه؟",
        "step2_skip": "🤷 ❓ تخطي/لا أعرف",
        "step2_error": "⚠️ ❌ تحتوي على خطأ/غير صحيحة",
        
        # Labeling - General
        "step1_completed": "تم إنجاز الخطوة الأولى. الآن يرجى تحديد أي دولة تمثل وجهة النظر هذه:",
        "annotation_saved": "✅ تم حفظ تصنيفك!",
        "milestone_10": "🎉 تهانينا! لقد صنفت 10 وجهات نظر! أنت تقوم بعمل رائع!",
        "milestone_25": "🌟 مذهل! لقد وصلت إلى 25 وجهة نظر! مساهمتك قيمة حقاً!",
        "milestone_40": "🏆 متميز! 40 وجهة نظر مصنفة! أنت تحدث تأثيراً كبيراً على بحثنا!",
        
        # Event grouping
        "event_group_info": "📚 <b>مجموعة الأحداث:</b> هذا الحدث يحتوي على {total} وجهة نظر. أنت في وجهة النظر {current} من {total}.",
        "next_viewpoint": "➡️ وجهة النظر التالية",
        "previous_viewpoint": "⬅️ وجهة النظر السابقة",
        "finish_event": "✅ إنهاء الحدث",
        "event_complete": "🎉 لقد أكملت جميع وجهات النظر لهذا الحدث! عمل رائع!",
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
        
        # Registration
        "registration_required": "⚠️ <b>التسجيل مطلوب</b>\n\nتحتاج إلى إكمال التسجيل قبل استخدام البوت. يرجى استخدام /start لبدء عملية التسجيل.",
        
        # Errors
        "error_general": "حدث خطأ. يرجى المحاولة مرة أخرى.",
    },
    
    "fr": {
        # Welcome and instructions
        "welcome": "<b>Bienvenue !</b>",
        "welcome_acknowledgment": "🎓 <b>Reconnaissance spéciale :</b> Les utilisateurs qui étiquettent 50 points de vue seront reconnus dans notre article de recherche !",
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
        "detailed_instructions_misinformation": "\n<b>🔍 Distinction importante : Désinformation vs. Erreurs</b>\nSi un point de vue contient de la désinformation qui semble être utilisée pour manipuler ou faire avancer un récit particulier, classez-le comme <b>biaisé</b> plutôt que comme une erreur. Ne marquez quelque chose comme 'erreur' que s'il contient des erreurs factuelles claires sans intention manipulatrice apparente.",
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
        "step1_neutral": "🟢 ✅ Neutre/Non biaisé",
        "step1_biased": "🔴 ⚖️ Position d'un pays/Biaisé", 
        "step1_error": "⚠️ ❌ Contient une erreur/Incorrect",
        
        # Labeling - Step 2
        "step2_instruction": "Quelle position de pays cela représente-t-il ?",
        "step2_skip": "🤷 ❓ Passer/Je ne sais pas",
        "step2_error": "⚠️ ❌ Contient une erreur/Incorrect",
        
        # Labeling - General
        "step1_completed": "Étape 1 terminée. Maintenant, veuillez spécifier quelle position de pays cela représente :",
        "annotation_saved": "✅ Votre annotation a été sauvegardée !",
        "milestone_10": "🎉 Félicitations ! Vous avez étiqueté 10 points de vue ! Vous faites un excellent travail !",
        "milestone_25": "🌟 Incroyable ! Vous avez atteint 25 points de vue ! Votre contribution est vraiment précieuse !",
        "milestone_40": "🏆 Exceptionnel ! 40 points de vue étiquetés ! Vous avez un impact significatif sur notre recherche !",
        
        # Event grouping
        "event_group_info": "📚 <b>Groupe d'événements :</b> Cet événement a {total} points de vue. Vous êtes au point de vue {current} sur {total}.",
        "next_viewpoint": "➡️ Point de vue suivant",
        "previous_viewpoint": "⬅️ Point de vue précédent",
        "finish_event": "✅ Terminer l'événement",
        "event_complete": "🎉 Vous avez terminé tous les points de vue pour cet événement ! Excellent travail !",
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
        
        # Registration
        "registration_required": "⚠️ <b>Inscription requise</b>\n\nVous devez compléter l'inscription avant d'utiliser le bot. Veuillez utiliser /start pour commencer le processus d'inscription.",
        
        # Errors
        "error_general": "Une erreur s'est produite. Veuillez réessayer.",
    },
    
    "he": {
        # Welcome and instructions
        "welcome": "<b>ברוכים הבאים!</b>",
        "welcome_acknowledgment": "🎓 <b>הכרה מיוחדת:</b> משתמשים שמתייגים 50 נקודות מבט יוזכרו במאמר המחקר שלנו!",
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
        "detailed_instructions_misinformation": "\n<b>🔍 הבחנה חשובה: דיסאינפורמציה מול שגיאות</b>\nאם נקודת מבט מכילה דיסאינפורמציה שנראית כמשמשת למניפולציה או לקידום נרטיב מסוים, סווגו אותה כ<b>מוטה</b> ולא כשגיאה. סמנו משהו כ'שגיאה' רק אם הוא מכיל טעויות עובדתיות ברורות ללא כוונה מניפולטיבית ברורה.",
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
        "step1_neutral": "🟢 ✅ נייטרלית/לא מוטה",
        "step1_biased": "🔴 ⚖️ עמדת מדינה/מוטה", 
        "step1_error": "⚠️ ❌ מכילה שגיאה/לא נכונה",
        
        # Labeling - Step 2
        "step2_instruction": "עמדה של איזו מדינה זה מייצג?",
        "step2_skip": "🤷 ❓ דלג/לא יודע",
        "step2_error": "⚠️ ❌ מכילה שגיאה/לא נכונה",
        
        # Labeling - General
        "step1_completed": "שלב 1 הושלם. עכשיו אנא ציינו עמדה של איזו מדינה זה מייצג:",
        "annotation_saved": "✅ הערת השילוב שלכם נשמרה!",
        "milestone_10": "🎉 מזל טוב! תייגתם 10 נקודות מבט! אתם עושים עבודה נהדרת!",
        "milestone_25": "🌟 מדהים! הגעתם ל-25 נקודות מבט! התרומה שלכם באמת יקרה!",
        "milestone_40": "🏆 יוצא דופן! 40 נקודות מבט מתויגות! אתם יוצרים השפעה משמעותית על המחקר שלנו!",
        
        # Event grouping
        "event_group_info": "📚 <b>קבוצת אירועים:</b> לאירוע הזה יש {total} נקודות מבט. אתם בנקודת המבט {current} מתוך {total}.",
        "next_viewpoint": "➡️ נקודת מבט הבאה",
        "previous_viewpoint": "⬅️ נקודת מבט קודמת",
        "finish_event": "✅ סיום אירוע",
        "event_complete": "🎉 סיימתם את כל נקודות המבט לאירוע הזה! עבודה מצוינת!",
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
        
        # Registration
        "registration_required": "⚠️ <b>נדרשת הרשמה</b>\n\nעליך להשלים את ההרשמה לפני השימוש בבוט. אנא השתמש ב-/start כדי להתחיל בתהליך ההרשמה.",
        
        # Errors
        "error_general": "אירעה שגיאה. אנא נסו שוב.",
    },
    
    "ru": {
        # Welcome and instructions
        "welcome": "<b>Добро пожаловать!</b>",
        "welcome_acknowledgment": "🎓 <b>Особое признание:</b> Пользователи, которые разметят 50 точек зрения, будут упомянуты в нашей исследовательской статье!",
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
        "detailed_instructions_misinformation": "\n<b>🔍 Важное различие: Дезинформация против ошибок</b>\nЕсли точка зрения содержит дезинформацию, которая, по-видимому, используется для манипуляций или продвижения определенного нарратива, классифицируйте её как <b>предвзятую</b>, а не как ошибку. Отмечайте что-то как 'ошибку' только если оно содержит явные фактические ошибки без видимого манипулятивного умысла.",
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
        "step1_neutral": "🟢 ✅ Нейтральной/Беспристрастной",
        "step1_biased": "🔴 ⚖️ Позицией страны/Пристрастной", 
        "step1_error": "⚠️ ❌ Содержит ошибку/Некорректно",
        
        # Labeling - Step 2
        "step2_instruction": "Позицию какой страны это представляет?",
        "step2_skip": "🤷 ❓ Пропустить/Не знаю",
        "step2_error": "⚠️ ❌ Содержит ошибку/Некорректно",
        
        # Labeling - General
        "step1_completed": "Шаг 1 завершен. Теперь пожалуйста укажите, позицию какой страны это представляет:",
        "annotation_saved": "✅ Ваша аннотация сохранена!",
        "milestone_10": "🎉 Поздравляем! Вы разметили 10 точек зрения! Вы отлично работаете!",
        "milestone_25": "🌟 Потрясающе! Вы достигли 25 точек зрения! Ваш вклад действительно ценен!",
        "milestone_40": "🏆 Выдающийся результат! 40 размеченных точек зрения! Вы оказываете значительное влияние на наше исследование!",
        
        # Event grouping
        "event_group_info": "📚 <b>Группа событий:</b> У этого события {total} точек зрения. Вы на точке зрения {current} из {total}.",
        "next_viewpoint": "➡️ Следующая точка зрения",
        "previous_viewpoint": "⬅️ Предыдущая точка зрения",
        "finish_event": "✅ Завершить событие",
        "event_complete": "🎉 Вы завершили все точки зрения для этого события! Отличная работа!",
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
        
        # Registration
        "registration_required": "⚠️ <b>Требуется регистрация</b>\n\nВам необходимо завершить регистрацию перед использованием бота. Пожалуйста, используйте /start для начала процесса регистрации.",
        
        # Errors
        "error_general": "Произошла ошибка. Пожалуйста, попробуйте снова.",
    },
    
    "zh": {
        # Welcome and instructions
        "welcome": "<b>欢迎！</b>",
        "welcome_acknowledgment": "🎓 <b>特别认可：</b> 标注50个观点的用户将在我们的研究论文中得到致谢！",
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
        "detailed_instructions_misinformation": "\n<b>🔍 重要区别：误导信息与错误</b>\n如果观点包含似乎用于操纵或推进特定叙述的误导信息，请将其归类为<b>有偏见的</b>而非错误。只有当内容包含明显的事实错误且没有明显操纵意图时，才标记为'错误'。",
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
        "step1_neutral": "🟢 ✅ 中性/无偏见",
        "step1_biased": "🔴 ⚖️ 国家立场/有偏见", 
        "step1_error": "⚠️ ❌ 包含错误/不正确",
        
        # Labeling - Step 2
        "step2_instruction": "这代表哪个国家的立场？",
        "step2_skip": "🤷 ❓ 跳过/不知道",
        "step2_error": "⚠️ ❌ 包含错误/不正确",
        
        # Labeling - General
        "step1_completed": "第1步完成。现在请指定这代表哪个国家的立场：",
        "annotation_saved": "✅ 您的标注已保存！",
        "milestone_10": "🎉 恭喜！您已标注了10个观点！您做得很好！",
        "milestone_25": "🌟 太棒了！您已达到25个观点！您的贡献非常有价值！",
        "milestone_40": "🏆 杰出！已标注40个观点！您对我们的研究产生了重大影响！",
        
        # Event grouping
        "event_group_info": "📚 <b>事件组：</b> 此事件有{total}个观点。您正在查看第{current}个观点，共{total}个。",
        "next_viewpoint": "➡️ 下一个观点",
        "previous_viewpoint": "⬅️ 上一个观点",
        "finish_event": "✅ 完成事件",
        "event_complete": "🎉 您已完成此事件的所有观点！做得很好！",
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
        
        # Registration
        "registration_required": "⚠️ <b>需要注册</b>\n\n您需要在使用机器人之前完成注册。请使用 /start 开始注册过程。",
        
        # Errors
        "error_general": "发生错误。请重试。",
    },
    
    "de": {
        # Welcome and instructions
        "welcome": "<b>Willkommen!</b>",
        "welcome_acknowledgment": "🎓 <b>Besondere Anerkennung:</b> Benutzer, die 50 Standpunkte kennzeichnen, werden in unserem Forschungsartikel erwähnt!",
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
        "detailed_instructions_misinformation": "\n<b>🔍 Wichtiger Unterschied: Desinformation vs. Fehler</b>\nWenn ein Standpunkt Desinformation enthält, die anscheinend zur Manipulation oder zur Förderung einer bestimmten Erzählung verwendet wird, klassifizieren Sie ihn als <b>voreingenommen</b> und nicht als Fehler. Markieren Sie etwas nur dann als 'Fehler', wenn es klare sachliche Fehler ohne erkennbare manipulative Absicht enthält.",
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
        "step1_neutral": "🟢 ✅ Neutral/Unvoreingenommen",
        "step1_biased": "🔴 ⚖️ Landesposition/Voreingenommen", 
        "step1_error": "⚠️ ❌ Enthält Fehler/Inkorrekt",
        
        # Labeling - Step 2
        "step2_instruction": "Welche Landesposition stellt dies dar?",
        "step2_skip": "🤷 ❓ Überspringen/Weiß nicht",
        "step2_error": "⚠️ ❌ Enthält Fehler/Inkorrekt",
        
        # Labeling - General
        "step1_completed": "Schritt 1 abgeschlossen. Bitte geben Sie nun an, welche Landesposition dies darstellt:",
        "annotation_saved": "✅ Ihre Annotation wurde gespeichert!",
        "milestone_10": "🎉 Herzlichen Glückwunsch! Sie haben 10 Standpunkte gekennzeichnet! Sie leisten großartige Arbeit!",
        "milestone_25": "🌟 Fantastisch! Sie haben 25 Standpunkte erreicht! Ihr Beitrag ist wirklich wertvoll!",
        "milestone_40": "🏆 Hervorragend! 40 Standpunkte gekennzeichnet! Sie haben einen bedeutenden Einfluss auf unsere Forschung!",
        
        # Event grouping
        "event_group_info": "📚 <b>Ereignisgruppe:</b> Dieses Ereignis hat {total} Standpunkte. Sie sind bei Standpunkt {current} von {total}.",
        "next_viewpoint": "➡️ Nächster Standpunkt",
        "previous_viewpoint": "⬅️ Vorheriger Standpunkt",
        "finish_event": "✅ Ereignis beenden",
        "event_complete": "🎉 Sie haben alle Standpunkte für dieses Ereignis abgeschlossen! Großartige Arbeit!",
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
        
        # Registration
        "registration_required": "⚠️ <b>Registrierung erforderlich</b>\n\nSie müssen die Registrierung abschließen, bevor Sie den Bot verwenden. Bitte verwenden Sie /start, um den Registrierungsprozess zu beginnen.",
        
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
