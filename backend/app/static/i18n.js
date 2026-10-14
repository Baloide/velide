'use strict';
const translationKeys = ['local', 'language', 'workspace', 'title', 'subtitle', 'windows',
  'settings', 'mode', 'tag', 'pseudonym', 'block', 'asterisk', 'modeHint', 'detect', 'names',
  'tax', 'dates', 'contacts', 'locations', 'ids', 'custom', 'customPlaceholder', 'customHint',
  'privacyTitle', 'privacyText', 'document', 'sample', 'clear', 'original', 'source', 'result',
  'review', 'inputPlaceholder', 'outputPlaceholder', 'auto', 'save', 'ai', 'copy', 'warning',
  'detections', 'footer', 'characters', 'removed', 'ready', 'processing', 'done', 'error',
  'copied', 'copyError', 'sampleError', 'prompt', 'items'
];
const translationRows = {
  it: [
    'Elaborazione locale', 'Lingua', 'PRIVACY CLINICA · SPAZIO DI LAVORO',
    'Proteggi i dati. Conserva il contesto.',
    'De-identifica i testi clinici sul tuo dispositivo, con controllo diretto su ogni sostituzione.',
    'Scarica per Windows', 'Impostazioni', 'Tipo di sostituzione', 'Etichette [TIPO]',
    'Pseudonimi coerenti', 'Bande nere ████', 'Asterischi ****',
    'I pseudonimi restano coerenti all’interno dello stesso documento.', 'Dati da riconoscere',
    'Nomi e professionisti', 'Codici fiscali e identificativi', 'Date', 'Telefoni ed email',
    'Indirizzi e strutture', 'Identificativi clinici', 'Termini aggiuntivi',
    'Un nome o termine per riga…', 'Aggiungi nomi, città o altri dati che vuoi oscurare.',
    'I dati restano qui',
    'Nessun servizio cloud. Testi elaborati localmente e non salvati dall’app.',
    'Documento clinico', 'Carica esempio', 'Pulisci', 'Testo originale', 'ORIGINALE',
    'Testo de-identificato', 'DA VERIFICARE', 'Incolla il referto o le note cliniche…',
    'Le sostituzioni appariranno qui mentre scrivi…', 'Elaborazione automatica', 'Salva .txt',
    'Copia per AI', 'Copia testo',
    'Verifica sempre il risultato prima di condividerlo. Le regole possono non riconoscere alcuni dati personali o rimuovere informazioni utili; la de-identificazione non garantisce anonimato.',
    'Verifica le sostituzioni', 'Sei lingue · Nessun servizio esterno', 'caratteri',
    'sostituzioni', 'In attesa del documento', 'Elaborazione in corso…',
    'Elaborazione completata · Verifica il risultato',
    'Elaborazione non riuscita. Verifica che il servizio locale sia attivo.',
    'Copiato negli appunti', 'Copia non riuscita. Seleziona e copia il testo manualmente.',
    'Impossibile caricare l’esempio.',
    'Riassumi il seguente testo clinico de-identificato, senza inventare dati mancanti. Evidenzia gli elementi clinici e le informazioni da verificare. Le sostituzioni indicano dati oscurati; non cercare di ricostruirli.',
    'elementi'
  ],
  en: [
    'Local processing', 'Language', 'CLINICAL PRIVACY · WORKSPACE',
    'Protect the data. Preserve the context.',
    'De-identify clinical text on your device, with direct control over every replacement.',
    'Download for Windows', 'Settings', 'Replacement style', 'Labels [TYPE]',
    'Consistent pseudonyms', 'Black bars ████', 'Asterisks ****',
    'Pseudonyms stay consistent within the same document.', 'Data to detect',
    'Names and professionals', 'Tax codes and identifiers', 'Dates', 'Phone numbers and email',
    'Addresses and facilities', 'Clinical identifiers', 'Additional terms',
    'One name or term per line…', 'Add names, cities or other information you want to mask.',
    'Your data stays here',
    'No cloud service. Text is processed locally and is not saved by the app.',
    'Clinical document', 'Load example', 'Clear', 'Original text', 'SOURCE',
    'De-identified text', 'REVIEW REQUIRED', 'Paste your clinical report or notes…',
    'Replacements appear here as you type…', 'Automatic processing', 'Save .txt', 'Copy for AI',
    'Copy text',
    'Always review the result before sharing it. Rules may miss personal information or remove useful details; de-identification does not guarantee anonymity.',
    'Review replacements', 'Six languages · No external services', 'characters', 'replacements',
    'Waiting for a document', 'Processing…', 'Processing complete · Review the result',
    'Processing failed. Check that the local service is running.', 'Copied to clipboard',
    'Copy failed. Select and copy the text manually.', 'Unable to load the example.',
    'Summarize the following de-identified clinical text without inventing missing data. Highlight clinical findings and information to verify. Replacements indicate masked data; do not try to reconstruct it.',
    'items'
  ],
  es: [
    'Procesamiento local', 'Idioma', 'PRIVACIDAD CLÍNICA · ESPACIO DE TRABAJO',
    'Protege los datos. Conserva el contexto.',
    'Desidentifica textos clínicos en tu dispositivo, con control directo sobre cada sustitución.',
    'Descargar para Windows', 'Configuración', 'Tipo de sustitución', 'Etiquetas [TIPO]',
    'Seudónimos coherentes', 'Barras negras ████', 'Asteriscos ****',
    'Los seudónimos se mantienen coherentes dentro del mismo documento.', 'Datos que detectar',
    'Nombres y profesionales', 'Códigos fiscales e identificadores', 'Fechas',
    'Teléfonos y correo', 'Direcciones y centros', 'Identificadores clínicos',
    'Términos adicionales', 'Un nombre o término por línea…',
    'Añade nombres, ciudades u otros datos que quieras ocultar.', 'Tus datos se quedan aquí',
    'Sin servicios en la nube. El texto se procesa localmente y la aplicación no lo guarda.',
    'Documento clínico', 'Cargar ejemplo', 'Limpiar', 'Texto original', 'ORIGINAL',
    'Texto desidentificado', 'REVISIÓN NECESARIA', 'Pega el informe o las notas clínicas…',
    'Las sustituciones aparecerán aquí mientras escribes…', 'Procesamiento automático',
    'Guardar .txt', 'Copiar para IA', 'Copiar texto',
    'Revisa siempre el resultado antes de compartirlo. Las reglas pueden omitir datos personales o eliminar información útil; la desidentificación no garantiza el anonimato.',
    'Revisar sustituciones', 'Seis idiomas · Sin servicios externos', 'caracteres',
    'sustituciones', 'Esperando un documento', 'Procesando…',
    'Procesamiento completado · Revisa el resultado',
    'Error de procesamiento. Comprueba que el servicio local esté activo.',
    'Copiado al portapapeles', 'No se pudo copiar. Selecciona y copia el texto manualmente.',
    'No se pudo cargar el ejemplo.',
    'Resume el siguiente texto clínico desidentificado sin inventar datos ausentes. Destaca los hallazgos clínicos y la información que debe verificarse. Las sustituciones indican datos ocultos; no intentes reconstruirlos.',
    'elementos'
  ],
  de: [
    'Lokale Verarbeitung', 'Sprache', 'KLINISCHER DATENSCHUTZ · ARBEITSBEREICH',
    'Daten schützen. Kontext bewahren.',
    'De-identifizieren Sie klinische Texte auf Ihrem Gerät und kontrollieren Sie jede Ersetzung.',
    'Für Windows herunterladen', 'Einstellungen', 'Ersetzungsart', 'Kennzeichnungen [TYP]',
    'Konsistente Pseudonyme', 'Schwarze Balken ████', 'Sternchen ****',
    'Pseudonyme bleiben innerhalb desselben Dokuments konsistent.', 'Zu erkennende Daten',
    'Namen und Fachpersonal', 'Steuernummern und Kennungen', 'Datumsangaben',
    'Telefon und E-Mail', 'Adressen und Einrichtungen', 'Klinische Kennungen',
    'Zusätzliche Begriffe', 'Ein Name oder Begriff pro Zeile…',
    'Ergänzen Sie Namen, Orte oder andere zu maskierende Angaben.', 'Ihre Daten bleiben hier',
    'Kein Cloud-Dienst. Texte werden lokal verarbeitet und von der App nicht gespeichert.',
    'Klinisches Dokument', 'Beispiel laden', 'Leeren', 'Originaltext', 'ORIGINAL',
    'De-identifizierter Text', 'PRÜFUNG ERFORDERLICH',
    'Bericht oder klinische Notizen hier einfügen…',
    'Ersetzungen erscheinen hier während der Eingabe…', 'Automatische Verarbeitung',
    '.txt speichern', 'Für KI kopieren', 'Text kopieren',
    'Prüfen Sie das Ergebnis vor der Weitergabe. Regeln können personenbezogene Daten übersehen oder nützliche Angaben entfernen; De-Identifizierung garantiert keine Anonymität.',
    'Ersetzungen prüfen', 'Sechs Sprachen · Keine externen Dienste', 'Zeichen', 'Ersetzungen',
    'Warten auf ein Dokument', 'Verarbeitung läuft…',
    'Verarbeitung abgeschlossen · Ergebnis prüfen',
    'Verarbeitung fehlgeschlagen. Prüfen Sie den lokalen Dienst.',
    'In die Zwischenablage kopiert',
    'Kopieren fehlgeschlagen. Text bitte manuell markieren und kopieren.',
    'Beispiel konnte nicht geladen werden.',
    'Fassen Sie den folgenden de-identifizierten klinischen Text zusammen, ohne fehlende Daten zu erfinden. Heben Sie klinische Befunde und zu überprüfende Angaben hervor. Ersetzungen kennzeichnen maskierte Daten; versuchen Sie nicht, diese zu rekonstruieren.',
    'Einträge'
  ],
  fr: [
    'Traitement local', 'Langue', 'CONFIDENTIALITÉ CLINIQUE · ESPACE DE TRAVAIL',
    'Protégez les données. Préservez le contexte.',
    'Désidentifiez les textes cliniques sur votre appareil, en contrôlant chaque remplacement.',
    'Télécharger pour Windows', 'Paramètres', 'Type de remplacement', 'Étiquettes [TYPE]',
    'Pseudonymes cohérents', 'Bandes noires ████', 'Astérisques ****',
    'Les pseudonymes restent cohérents dans un même document.', 'Données à détecter',
    'Noms et professionnels', 'Codes fiscaux et identifiants', 'Dates', 'Téléphones et e-mails',
    'Adresses et établissements', 'Identifiants cliniques', 'Termes supplémentaires',
    'Un nom ou terme par ligne…',
    'Ajoutez des noms, des villes ou toute autre donnée à masquer.', 'Vos données restent ici',
    'Aucun service cloud. Les textes sont traités localement et ne sont pas enregistrés par l’application.',
    'Document clinique', 'Charger un exemple', 'Effacer', 'Texte original', 'ORIGINAL',
    'Texte désidentifié', 'À VÉRIFIER', 'Collez le compte rendu ou les notes cliniques…',
    'Les remplacements apparaîtront ici pendant la saisie…', 'Traitement automatique',
    'Enregistrer .txt', 'Copier pour l’IA', 'Copier le texte',
    'Vérifiez toujours le résultat avant de le partager. Les règles peuvent manquer des données personnelles ou supprimer des informations utiles ; la désidentification ne garantit pas l’anonymat.',
    'Vérifier les remplacements', 'Six langues · Aucun service externe', 'caractères',
    'remplacements', 'En attente d’un document', 'Traitement en cours…',
    'Traitement terminé · Vérifiez le résultat',
    'Échec du traitement. Vérifiez que le service local est actif.',
    'Copié dans le presse-papiers',
    'Échec de la copie. Sélectionnez et copiez le texte manuellement.',
    'Impossible de charger l’exemple.',
    'Résumez le texte clinique désidentifié suivant sans inventer de données manquantes. Soulignez les constatations cliniques et les informations à vérifier. Les remplacements signalent des données masquées ; ne tentez pas de les reconstituer.',
    'éléments'
  ],
  pt: [
    'Processamento local', 'Idioma', 'PRIVACIDADE CLÍNICA · ÁREA DE TRABALHO',
    'Proteja os dados. Preserve o contexto.',
    'Desidentifique textos clínicos no seu dispositivo, com controlo direto de cada substituição.',
    'Transferir para Windows', 'Definições', 'Tipo de substituição', 'Etiquetas [TIPO]',
    'Pseudónimos coerentes', 'Barras pretas ████', 'Asteriscos ****',
    'Os pseudónimos mantêm-se coerentes no mesmo documento.', 'Dados a detetar',
    'Nomes e profissionais', 'Códigos fiscais e identificadores', 'Datas', 'Telefones e email',
    'Moradas e instituições', 'Identificadores clínicos', 'Termos adicionais',
    'Um nome ou termo por linha…',
    'Adicione nomes, cidades ou outros dados que queira ocultar.', 'Os dados ficam aqui',
    'Sem serviços na nuvem. Os textos são processados localmente e não são guardados pela aplicação.',
    'Documento clínico', 'Carregar exemplo', 'Limpar', 'Texto original', 'ORIGINAL',
    'Texto desidentificado', 'REVISÃO NECESSÁRIA', 'Cole o relatório ou as notas clínicas…',
    'As substituições aparecerão aqui enquanto escreve…', 'Processamento automático',
    'Guardar .txt', 'Copiar para IA', 'Copiar texto',
    'Reveja sempre o resultado antes de o partilhar. As regras podem não detetar dados pessoais ou remover informações úteis; a desidentificação não garante anonimato.',
    'Rever substituições', 'Seis idiomas · Sem serviços externos', 'caracteres',
    'substituições', 'À espera de um documento', 'A processar…',
    'Processamento concluído · Reveja o resultado',
    'Falha no processamento. Verifique se o serviço local está ativo.',
    'Copiado para a área de transferência',
    'Falha ao copiar. Selecione e copie o texto manualmente.',
    'Não foi possível carregar o exemplo.',
    'Resuma o seguinte texto clínico desidentificado sem inventar dados em falta. Destaque os elementos clínicos e as informações a verificar. As substituições indicam dados ocultos; não tente reconstruí-los.',
    'elementos'
  ]
};
translationRows.nl = [
  'Lokale verwerking', 'Taal', 'KLINISCHE PRIVACY · WERKRUIMTE',
  'Bescherm de gegevens. Behoud de context.',
  'De-identificeer klinische teksten op uw apparaat, met controle over elke vervanging.',
  'Downloaden voor Windows', 'Instellingen', 'Vervangingswijze', 'Labels [TYPE]',
  'Consistente pseudoniemen', 'Zwarte balken ████', 'Sterretjes ****',
  'Pseudoniemen blijven consistent binnen hetzelfde document.', 'Te herkennen gegevens',
  'Namen en zorgverleners', 'Belastingnummers en identificatoren', 'Datums', 'Telefoon en e-mail',
  'Adressen en instellingen', 'Klinische identificatoren', 'Extra termen',
  'Eén naam of term per regel…', 'Voeg namen, plaatsen of andere te verbergen gegevens toe.',
  'Uw gegevens blijven hier',
  'Geen clouddienst. Teksten worden lokaal verwerkt en niet door de app opgeslagen.',
  'Klinisch document', 'Voorbeeld laden', 'Wissen', 'Originele tekst', 'ORIGINEEL',
  'Gede-identificeerde tekst', 'CONTROLE NODIG', 'Plak het verslag of de klinische notities…',
  'Vervangingen verschijnen hier terwijl u typt…', 'Automatische verwerking', '.txt opslaan',
  'Kopiëren voor AI', 'Tekst kopiëren',
  'Controleer het resultaat altijd voordat u het deelt. Regels kunnen persoonsgegevens missen of nuttige informatie verwijderen; de-identificatie garandeert geen anonimiteit.',
  'Vervangingen controleren', '10 talen · Geen externe diensten', 'tekens', 'vervangingen',
  'Wachten op een document', 'Bezig met verwerken…',
  'Verwerking voltooid · Controleer het resultaat',
  'Verwerking mislukt. Controleer of de lokale dienst actief is.', 'Gekopieerd naar het klembord',
  'Kopiëren mislukt. Selecteer en kopieer de tekst handmatig.',
  'Het voorbeeld kon niet worden geladen.',
  'Vat de volgende gede-identificeerde klinische tekst samen zonder ontbrekende gegevens te verzinnen. Benoem klinische bevindingen en informatie die moet worden gecontroleerd. Vervangingen duiden op verborgen gegevens; probeer deze niet te reconstrueren.',
  'items'
];
translationRows.pl = [
  'Przetwarzanie lokalne', 'Język', 'PRYWATNOŚĆ KLINICZNA · OBSZAR ROBOCZY',
  'Chroń dane. Zachowaj kontekst.',
  'Usuwaj dane identyfikujące z tekstów klinicznych na swoim urządzeniu, kontrolując każde zastąpienie.',
  'Pobierz dla Windows', 'Ustawienia', 'Sposób zastępowania', 'Etykiety [TYP]',
  'Spójne pseudonimy', 'Czarne paski ████', 'Gwiazdki ****',
  'Pseudonimy pozostają spójne w obrębie tego samego dokumentu.', 'Dane do wykrycia',
  'Nazwiska i personel', 'Numery podatkowe i identyfikatory', 'Daty', 'Telefony i e-mail',
  'Adresy i placówki', 'Identyfikatory kliniczne', 'Dodatkowe terminy',
  'Jedno nazwisko lub termin w wierszu…',
  'Dodaj nazwiska, miejscowości lub inne dane do ukrycia.', 'Dane pozostają tutaj',
  'Bez usług w chmurze. Teksty są przetwarzane lokalnie i nie są zapisywane przez aplikację.',
  'Dokument kliniczny', 'Wczytaj przykład', 'Wyczyść', 'Tekst oryginalny', 'ORYGINAŁ',
  'Tekst po deidentyfikacji', 'WYMAGA WERYFIKACJI', 'Wklej raport lub notatki kliniczne…',
  'Zastąpienia pojawią się tutaj podczas pisania…', 'Przetwarzanie automatyczne', 'Zapisz .txt',
  'Kopiuj dla AI', 'Kopiuj tekst',
  'Zawsze sprawdzaj wynik przed udostępnieniem. Reguły mogą pominąć dane osobowe lub usunąć przydatne informacje; deidentyfikacja nie gwarantuje anonimowości.',
  'Sprawdź zastąpienia', '10 języków · Bez usług zewnętrznych', 'znaków', 'zastąpień',
  'Oczekiwanie na dokument', 'Przetwarzanie…', 'Przetwarzanie zakończone · Sprawdź wynik',
  'Przetwarzanie nie powiodło się. Sprawdź, czy usługa lokalna działa.', 'Skopiowano do schowka',
  'Kopiowanie nie powiodło się. Zaznacz i skopiuj tekst ręcznie.', 'Nie można wczytać przykładu.',
  'Podsumuj poniższy tekst kliniczny po deidentyfikacji bez wymyślania brakujących danych. Wskaż ustalenia kliniczne i informacje do weryfikacji. Zastąpienia oznaczają ukryte dane; nie próbuj ich odtwarzać.',
  'elementów'
];
translationRows.tr = [
  'Yerel işleme', 'Dil', 'KLİNİK GİZLİLİK · ÇALIŞMA ALANI',
  'Verileri koruyun. Bağlamı muhafaza edin.',
  'Klinik metinlerdeki kimlik bilgilerini cihazınızda kaldırın ve her değişikliği kontrol edin.',
  'Windows için indir', 'Ayarlar', 'Değiştirme biçimi', 'Etiketler [TÜR]', 'Tutarlı takma adlar',
  'Siyah çubuklar ████', 'Yıldızlar ****', 'Takma adlar aynı belge içinde tutarlı kalır.',
  'Tespit edilecek veriler', 'Adlar ve sağlık çalışanları', 'Vergi numaraları ve kimlikler',
  'Tarihler', 'Telefon ve e-posta', 'Adresler ve kuruluşlar', 'Klinik kimlikler', 'Ek terimler',
  'Her satıra bir ad veya terim…',
  'Gizlemek istediğiniz adları, şehirleri veya diğer bilgileri ekleyin.',
  'Verileriniz burada kalır',
  'Bulut hizmeti yok. Metinler yerel olarak işlenir ve uygulama tarafından kaydedilmez.',
  'Klinik belge', 'Örnek yükle', 'Temizle', 'Orijinal metin', 'ORİJİNAL',
  'Kimlik bilgileri kaldırılmış metin', 'KONTROL GEREKLİ',
  'Raporu veya klinik notları yapıştırın…', 'Değişiklikler yazarken burada görünür…',
  'Otomatik işleme', '.txt kaydet', 'Yapay zekâ için kopyala', 'Metni kopyala',
  'Paylaşmadan önce sonucu mutlaka kontrol edin. Kurallar kişisel bilgileri atlayabilir veya yararlı bilgileri kaldırabilir; kimlik bilgilerinin kaldırılması anonimliği garanti etmez.',
  'Değişiklikleri incele', '10 dil · Harici hizmet yok', 'karakter', 'değişiklik',
  'Belge bekleniyor', 'İşleniyor…', 'İşleme tamamlandı · Sonucu kontrol edin',
  'İşleme başarısız. Yerel hizmetin çalıştığını kontrol edin.', 'Panoya kopyalandı',
  'Kopyalama başarısız. Metni seçip elle kopyalayın.', 'Örnek yüklenemedi.',
  'Aşağıdaki kimlik bilgileri kaldırılmış klinik metni eksik veriler uydurmadan özetleyin. Klinik bulguları ve doğrulanması gereken bilgileri vurgulayın. Değişiklikler gizlenen verileri gösterir; bunları yeniden oluşturmaya çalışmayın.',
  'öğe'
];
translationRows.ru = [
  'Локальная обработка', 'Язык', 'КОНФИДЕНЦИАЛЬНОСТЬ · РАБОЧАЯ ОБЛАСТЬ',
  'Защитите данные. Сохраните контекст.',
  'Удаляйте идентифицирующие данные из клинических текстов на своём устройстве, контролируя каждую замену.',
  'Скачать для Windows', 'Настройки', 'Способ замены', 'Метки [ТИП]', 'Согласованные псевдонимы',
  'Чёрные полосы ████', 'Звёздочки ****',
  'Псевдонимы остаются согласованными в пределах одного документа.', 'Данные для обнаружения',
  'Имена и специалисты', 'Налоговые номера и идентификаторы', 'Даты',
  'Телефоны и электронная почта', 'Адреса и учреждения', 'Клинические идентификаторы',
  'Дополнительные термины', 'Одно имя или термин в каждой строке…',
  'Добавьте имена, города или другие данные для скрытия.', 'Ваши данные остаются здесь',
  'Без облачных сервисов. Тексты обрабатываются локально и не сохраняются приложением.',
  'Клинический документ', 'Загрузить пример', 'Очистить', 'Исходный текст', 'ОРИГИНАЛ',
  'Обезличенный текст', 'ТРЕБУЕТ ПРОВЕРКИ', 'Вставьте заключение или клинические заметки…',
  'Замены появятся здесь во время ввода…', 'Автоматическая обработка', 'Сохранить .txt',
  'Копировать для ИИ', 'Копировать текст',
  'Всегда проверяйте результат перед передачей. Правила могут пропустить персональные данные или удалить полезную информацию; обезличивание не гарантирует анонимности.',
  'Проверить замены', '10 языков · Без внешних сервисов', 'символов', 'замен',
  'Ожидание документа', 'Обработка…', 'Обработка завершена · Проверьте результат',
  'Ошибка обработки. Убедитесь, что локальный сервис работает.', 'Скопировано в буфер обмена',
  'Не удалось скопировать. Выделите и скопируйте текст вручную.', 'Не удалось загрузить пример.',
  'Составьте краткое изложение следующего обезличенного клинического текста, не выдумывая отсутствующие данные. Выделите клинические находки и информацию, требующую проверки. Замены обозначают скрытые данные; не пытайтесь их восстановить.',
  'элементов'
];

const appearanceTranslations = {
  it: {
    appearance: 'Aspetto',
    system: 'Sistema',
    light: 'Giorno',
    dark: 'Notte',
    footer: '10 lingue · Nessun servizio esterno'
  },
  en: {
    appearance: 'Appearance',
    system: 'System',
    light: 'Day',
    dark: 'Night',
    footer: '10 languages · No external services'
  },
  es: {
    appearance: 'Apariencia',
    system: 'Sistema',
    light: 'Día',
    dark: 'Noche',
    footer: '10 idiomas · Sin servicios externos'
  },
  de: {
    appearance: 'Darstellung',
    system: 'System',
    light: 'Tag',
    dark: 'Nacht',
    footer: '10 Sprachen · Keine externen Dienste'
  },
  fr: {
    appearance: 'Apparence',
    system: 'Système',
    light: 'Jour',
    dark: 'Nuit',
    footer: '10 langues · Aucun service externe'
  },
  pt: {
    appearance: 'Aparência',
    system: 'Sistema',
    light: 'Dia',
    dark: 'Noite',
    footer: '10 idiomas · Sem serviços externos'
  },
  nl: {
    appearance: 'Weergave',
    system: 'Systeem',
    light: 'Dag',
    dark: 'Nacht'
  },
  pl: {
    appearance: 'Wygląd',
    system: 'System',
    light: 'Dzień',
    dark: 'Noc'
  },
  tr: {
    appearance: 'Görünüm',
    system: 'Sistem',
    light: 'Gündüz',
    dark: 'Gece'
  },
  ru: {
    appearance: 'Оформление',
    system: 'Система',
    light: 'День',
    dark: 'Ночь'
  }
};

const uploadKeys = ['dropFile', 'chooseFile', 'uploadHint', 'importingFile', 'fileImported',
  'importFailed', 'oneFileOnly', 'fileTooLarge', 'unsupportedFile', 'emptyFile', 'unreadableFile',
  'encryptedPdf', 'pdfNoText', 'tooManyPages', 'textTooLong', 'textEncoding',
  'documentTooComplex', 'importReview', 'partialPdf', 'docxReview'
];
const uploadRows = {
  it: ['Trascina qui un documento', 'Scegli file', 'PDF, DOCX, TXT, MD · Max 10 MB · Solo locale',
    'Estrazione del testo in corso…', 'Documento importato',
    'Importazione non riuscita. Il testo precedente è conservato; verifica il servizio locale.',
    'Carica un solo file alla volta.', 'Il file supera il limite di 10 MB.',
    'Formato non supportato. Usa PDF, DOCX, TXT o MD.',
    'Il file è vuoto o non contiene testo leggibile.',
    'Il file è danneggiato o non è un documento valido nel formato scelto.',
    'Il PDF è protetto. Esporta una copia non cifrata dal programma di origine.',
    'Il PDF non contiene testo estraibile. Potrebbe essere una scansione: serve OCR, non ancora disponibile.',
    'Il PDF supera il limite di 200 pagine.',
    'Il testo estratto supera il limite di 200.000 caratteri.',
    'Il testo non è leggibile. Usa UTF-8, UTF-16 con BOM o Windows-1252.',
    'Il documento è troppo complesso per essere importato. Dividilo o esportalo in testo semplice.',
    'Controlla il testo estratto: impaginazione e ordine di lettura possono cambiare. Il file originale non viene modificato.',
    'Alcune pagine non hanno testo estraibile e possono richiedere OCR. Controlla il documento originale.',
    'Per DOCX sono inclusi paragrafi, tabelle, intestazioni e piè di pagina. Immagini, note, caselle di testo e revisioni possono non essere importate.'
  ],
  en: ['Drop a document here', 'Choose file', 'PDF, DOCX, TXT, MD · Max 10 MB · Local only',
    'Extracting text…', 'Document imported',
    'Import failed. The previous text is preserved; check the local service.',
    'Upload one file at a time.', 'The file exceeds the 10 MB limit.',
    'Unsupported format. Use PDF, DOCX, TXT or MD.',
    'The file is empty or contains no readable text.',
    'The file is damaged or is not a valid document in the selected format.',
    'The PDF is encrypted. Export an unencrypted copy from the source application.',
    'The PDF contains no extractable text. It may be a scan and require OCR, which is not available yet.',
    'The PDF exceeds the 200-page limit.',
    'Extracted text exceeds the 200,000-character limit.',
    'Text cannot be decoded. Use UTF-8, UTF-16 with a BOM or Windows-1252.',
    'The document is too complex to import. Split it or export plain text.',
    'Review the extracted text: layout and reading order may change. The original file is unchanged.',
    'Some pages have no extractable text and may require OCR. Check the original document.',
    'DOCX includes paragraphs, tables, headers and footers. Images, notes, text boxes and tracked changes may not be imported.'
  ],
  es: ['Arrastra un documento aquí', 'Elegir archivo',
    'PDF, DOCX, TXT, MD · Máx. 10 MB · Solo local', 'Extrayendo texto…', 'Documento importado',
    'Error de importación. El texto anterior se conserva; comprueba el servicio local.',
    'Carga un solo archivo cada vez.', 'El archivo supera el límite de 10 MB.',
    'Formato no compatible. Usa PDF, DOCX, TXT o MD.',
    'El archivo está vacío o no contiene texto legible.',
    'El archivo está dañado o no es un documento válido en el formato seleccionado.',
    'El PDF está cifrado. Exporta una copia sin cifrar desde la aplicación original.',
    'El PDF no contiene texto extraíble. Puede ser un escaneo y necesitar OCR, aún no disponible.',
    'El PDF supera el límite de 200 páginas.',
    'El texto extraído supera los 200.000 caracteres.',
    'El texto no se puede leer. Usa UTF-8, UTF-16 con BOM o Windows-1252.',
    'El documento es demasiado complejo. Divídelo o expórtalo como texto plano.',
    'Revisa el texto extraído: el formato y el orden de lectura pueden cambiar. El archivo original no se modifica.',
    'Algunas páginas no tienen texto extraíble y pueden necesitar OCR. Revisa el documento original.',
    'DOCX incluye párrafos, tablas, encabezados y pies de página. Las imágenes, notas, cuadros de texto y revisiones pueden no importarse.'
  ],
  de: ['Dokument hier ablegen', 'Datei auswählen', 'PDF, DOCX, TXT, MD · Max. 10 MB · Nur lokal',
    'Text wird extrahiert…', 'Dokument importiert',
    'Import fehlgeschlagen. Der bisherige Text bleibt erhalten; prüfen Sie den lokalen Dienst.',
    'Laden Sie jeweils eine Datei hoch.', 'Die Datei überschreitet 10 MB.',
    'Format nicht unterstützt. Verwenden Sie PDF, DOCX, TXT oder MD.',
    'Die Datei ist leer oder enthält keinen lesbaren Text.',
    'Die Datei ist beschädigt oder kein gültiges Dokument im gewählten Format.',
    'Das PDF ist verschlüsselt. Exportieren Sie eine unverschlüsselte Kopie aus der ursprünglichen Anwendung.',
    'Das PDF enthält keinen extrahierbaren Text. Möglicherweise ist es ein Scan und benötigt OCR, das noch nicht verfügbar ist.',
    'Das PDF überschreitet 200 Seiten.', 'Der extrahierte Text überschreitet 200.000 Zeichen.',
    'Der Text kann nicht gelesen werden. Verwenden Sie UTF-8, UTF-16 mit BOM oder Windows-1252.',
    'Das Dokument ist zu komplex. Teilen Sie es auf oder exportieren Sie reinen Text.',
    'Prüfen Sie den extrahierten Text: Layout und Lesereihenfolge können sich ändern. Die Originaldatei bleibt unverändert.',
    'Einige Seiten enthalten keinen extrahierbaren Text und benötigen möglicherweise OCR. Prüfen Sie das Original.',
    'DOCX umfasst Absätze, Tabellen, Kopf- und Fußzeilen. Bilder, Anmerkungen, Textfelder und Änderungen werden möglicherweise nicht importiert.'
  ],
  fr: ['Déposez un document ici', 'Choisir un fichier',
    'PDF, DOCX, TXT, MD · Max. 10 Mo · Local uniquement', 'Extraction du texte…',
    'Document importé',
    'Échec de l’importation. Le texte précédent est conservé ; vérifiez le service local.',
    'Importez un seul fichier à la fois.', 'Le fichier dépasse la limite de 10 Mo.',
    'Format non pris en charge. Utilisez PDF, DOCX, TXT ou MD.',
    'Le fichier est vide ou ne contient aucun texte lisible.',
    'Le fichier est endommagé ou n’est pas valide dans le format choisi.',
    'Le PDF est chiffré. Exportez une copie non chiffrée depuis l’application d’origine.',
    'Le PDF ne contient aucun texte extractible. Il peut s’agir d’un scan nécessitant un OCR, pas encore disponible.',
    'Le PDF dépasse la limite de 200 pages.', 'Le texte extrait dépasse 200 000 caractères.',
    'Le texte ne peut pas être lu. Utilisez UTF-8, UTF-16 avec BOM ou Windows-1252.',
    'Le document est trop complexe. Divisez-le ou exportez-le en texte brut.',
    'Vérifiez le texte extrait : la mise en page et l’ordre de lecture peuvent changer. Le fichier original reste inchangé.',
    'Certaines pages n’ont aucun texte extractible et peuvent nécessiter un OCR. Vérifiez le document original.',
    'DOCX inclut paragraphes, tableaux, en-têtes et pieds de page. Images, notes, zones de texte et révisions peuvent ne pas être importées.'
  ],
  pt: ['Arraste um documento para aqui', 'Escolher ficheiro',
    'PDF, DOCX, TXT, MD · Máx. 10 MB · Apenas local', 'A extrair texto…', 'Documento importado',
    'Falha na importação. O texto anterior é mantido; verifique o serviço local.',
    'Carregue um ficheiro de cada vez.', 'O ficheiro excede o limite de 10 MB.',
    'Formato não suportado. Use PDF, DOCX, TXT ou MD.',
    'O ficheiro está vazio ou não contém texto legível.',
    'O ficheiro está danificado ou não é válido no formato selecionado.',
    'O PDF está encriptado. Exporte uma cópia não encriptada a partir da aplicação original.',
    'O PDF não contém texto extraível. Pode ser uma digitalização e precisar de OCR, ainda não disponível.',
    'O PDF excede o limite de 200 páginas.', 'O texto extraído excede os 200.000 caracteres.',
    'O texto não pode ser lido. Use UTF-8, UTF-16 com BOM ou Windows-1252.',
    'O documento é demasiado complexo. Divida-o ou exporte texto simples.',
    'Reveja o texto extraído: a formatação e a ordem de leitura podem mudar. O ficheiro original não é alterado.',
    'Algumas páginas não têm texto extraível e podem precisar de OCR. Verifique o documento original.',
    'DOCX inclui parágrafos, tabelas, cabeçalhos e rodapés. Imagens, notas, caixas de texto e revisões podem não ser importadas.'
  ],
  nl: ['Sleep hier een document', 'Bestand kiezen',
    'PDF, DOCX, TXT, MD · Max. 10 MB · Alleen lokaal', 'Tekst wordt uitgelezen…',
    'Document geïmporteerd',
    'Importeren mislukt. De vorige tekst blijft behouden; controleer de lokale dienst.',
    'Upload één bestand tegelijk.', 'Het bestand is groter dan 10 MB.',
    'Formaat niet ondersteund. Gebruik PDF, DOCX, TXT of MD.',
    'Het bestand is leeg of bevat geen leesbare tekst.',
    'Het bestand is beschadigd of ongeldig voor het gekozen formaat.',
    'De PDF is versleuteld. Exporteer een niet-versleutelde kopie vanuit de oorspronkelijke toepassing.',
    'De PDF bevat geen uitleesbare tekst. Mogelijk is het een scan waarvoor OCR nodig is; dit is nog niet beschikbaar.',
    'De PDF bevat meer dan 200 pagina’s.', 'De uitgelezen tekst bevat meer dan 200.000 tekens.',
    'De tekst kan niet worden gelezen. Gebruik UTF-8, UTF-16 met BOM of Windows-1252.',
    'Het document is te complex. Splits het of exporteer platte tekst.',
    'Controleer de uitgelezen tekst: opmaak en leesvolgorde kunnen veranderen. Het oorspronkelijke bestand blijft ongewijzigd.',
    'Sommige pagina’s bevatten geen uitleesbare tekst en vereisen mogelijk OCR. Controleer het oorspronkelijke document.',
    'DOCX omvat alinea’s, tabellen, kop- en voetteksten. Afbeeldingen, notities, tekstvakken en bijgehouden wijzigingen worden mogelijk niet geïmporteerd.'
  ],
  pl: ['Przeciągnij dokument tutaj', 'Wybierz plik',
    'PDF, DOCX, TXT, MD · Maks. 10 MB · Tylko lokalnie', 'Wyodrębnianie tekstu…',
    'Dokument zaimportowany',
    'Import nie powiódł się. Poprzedni tekst zachowano; sprawdź usługę lokalną.',
    'Prześlij jeden plik naraz.', 'Plik przekracza limit 10 MB.',
    'Nieobsługiwany format. Użyj PDF, DOCX, TXT lub MD.',
    'Plik jest pusty lub nie zawiera czytelnego tekstu.',
    'Plik jest uszkodzony lub nieprawidłowy dla wybranego formatu.',
    'PDF jest zaszyfrowany. Wyeksportuj niezaszyfrowaną kopię z aplikacji źródłowej.',
    'PDF nie zawiera tekstu do wyodrębnienia. Może być skanem wymagającym OCR, które nie jest jeszcze dostępne.',
    'PDF przekracza limit 200 stron.', 'Wyodrębniony tekst przekracza 200 000 znaków.',
    'Nie można odczytać tekstu. Użyj UTF-8, UTF-16 z BOM lub Windows-1252.',
    'Dokument jest zbyt złożony. Podziel go lub wyeksportuj zwykły tekst.',
    'Sprawdź wyodrębniony tekst: układ i kolejność czytania mogą się zmienić. Plik oryginalny nie jest modyfikowany.',
    'Niektóre strony nie zawierają tekstu do wyodrębnienia i mogą wymagać OCR. Sprawdź dokument oryginalny.',
    'DOCX obejmuje akapity, tabele, nagłówki i stopki. Obrazy, przypisy, pola tekstowe i śledzone zmiany mogą nie zostać zaimportowane.'
  ],
  tr: ['Belgeyi buraya sürükleyin', 'Dosya seç',
    'PDF, DOCX, TXT, MD · En fazla 10 MB · Yalnızca yerel', 'Metin çıkarılıyor…',
    'Belge içe aktarıldı',
    'İçe aktarma başarısız. Önceki metin korunuyor; yerel hizmeti kontrol edin.',
    'Her seferinde bir dosya yükleyin.', 'Dosya 10 MB sınırını aşıyor.',
    'Desteklenmeyen biçim. PDF, DOCX, TXT veya MD kullanın.',
    'Dosya boş veya okunabilir metin içermiyor.',
    'Dosya hasarlı veya seçilen biçimde geçerli değil.',
    'PDF şifreli. Kaynak uygulamadan şifrelenmemiş bir kopya dışa aktarın.',
    'PDF çıkarılabilir metin içermiyor. OCR gerektiren bir tarama olabilir; OCR henüz mevcut değil.',
    'PDF 200 sayfa sınırını aşıyor.', 'Çıkarılan metin 200.000 karakter sınırını aşıyor.',
    'Metin okunamıyor. UTF-8, BOM içeren UTF-16 veya Windows-1252 kullanın.',
    'Belge çok karmaşık. Bölün veya düz metin olarak dışa aktarın.',
    'Çıkarılan metni kontrol edin: düzen ve okuma sırası değişebilir. Orijinal dosya değiştirilmez.',
    'Bazı sayfalarda çıkarılabilir metin yok ve OCR gerekebilir. Orijinal belgeyi kontrol edin.',
    'DOCX paragrafları, tabloları, üstbilgileri ve altbilgileri içerir. Görseller, notlar, metin kutuları ve izlenen değişiklikler içe aktarılmayabilir.'
  ],
  ru: ['Перетащите документ сюда', 'Выбрать файл',
    'PDF, DOCX, TXT, MD · До 10 МБ · Только локально', 'Извлечение текста…',
    'Документ импортирован',
    'Ошибка импорта. Предыдущий текст сохранён; проверьте локальный сервис.',
    'Загружайте по одному файлу.', 'Файл превышает ограничение 10 МБ.',
    'Формат не поддерживается. Используйте PDF, DOCX, TXT или MD.',
    'Файл пуст или не содержит читаемого текста.',
    'Файл повреждён или недействителен для выбранного формата.',
    'PDF зашифрован. Экспортируйте незашифрованную копию из исходного приложения.',
    'PDF не содержит извлекаемого текста. Возможно, это скан, требующий OCR, которое пока недоступно.',
    'PDF превышает ограничение в 200 страниц.', 'Извлечённый текст превышает 200 000 символов.',
    'Текст не удаётся прочитать. Используйте UTF-8, UTF-16 с BOM или Windows-1252.',
    'Документ слишком сложный. Разделите его или экспортируйте простой текст.',
    'Проверьте извлечённый текст: форматирование и порядок чтения могут измениться. Исходный файл не изменяется.',
    'На некоторых страницах нет извлекаемого текста; возможно, требуется OCR. Проверьте исходный документ.',
    'DOCX включает абзацы, таблицы, колонтитулы. Изображения, примечания, текстовые поля и исправления могут не импортироваться.'
  ]
};
const uploadTranslations = Object.fromEntries(Object.entries(uploadRows).map(([language, row]) => {
  if (row.length !== uploadKeys.length) throw new Error(
    `Incomplete upload translation: ${language}`);
  return [language, Object.fromEntries(uploadKeys.map((key, i) => [key, row[i]]))];
}));

const importServiceTranslations = {
  it: {
    serviceOutdated: 'Il servizio locale è una versione precedente senza importazione file. Chiudilo e riavvialo dalla cartella aggiornata, poi riprova.',
    importStopped: 'Caricamento interrotto · Controlla il messaggio nel pannello originale'
  },
  en: {
    serviceOutdated: 'The local service is an older version without file import. Close it and restart it from the updated folder, then try again.',
    importStopped: 'Upload stopped · Check the message in the original-text panel'
  },
  es: {
    serviceOutdated: 'El servicio local es una versión anterior sin importación de archivos. Ciérralo y reinícialo desde la carpeta actualizada.',
    importStopped: 'Carga interrumpida · Revisa el mensaje en el panel original'
  },
  de: {
    serviceOutdated: 'Der lokale Dienst ist eine ältere Version ohne Dateiimport. Beenden Sie ihn und starten Sie ihn aus dem aktualisierten Ordner neu.',
    importStopped: 'Upload unterbrochen · Meldung im Originaltext prüfen'
  },
  fr: {
    serviceOutdated: 'Le service local est une ancienne version sans importation de fichiers. Fermez-le et relancez-le depuis le dossier mis à jour.',
    importStopped: 'Chargement interrompu · Consultez le message dans le panneau original'
  },
  pt: {
    serviceOutdated: 'O serviço local é uma versão anterior sem importação de ficheiros. Feche-o e reinicie-o a partir da pasta atualizada.',
    importStopped: 'Carregamento interrompido · Veja a mensagem no painel original'
  },
  nl: {
    serviceOutdated: 'De lokale dienst is een oudere versie zonder bestandsimport. Sluit deze en start opnieuw vanuit de bijgewerkte map.',
    importStopped: 'Upload gestopt · Bekijk de melding bij de originele tekst'
  },
  pl: {
    serviceOutdated: 'Usługa lokalna jest starszą wersją bez importowania plików. Zamknij ją i uruchom ponownie z zaktualizowanego folderu.',
    importStopped: 'Przesyłanie przerwane · Sprawdź komunikat w panelu oryginału'
  },
  tr: {
    serviceOutdated: 'Yerel hizmet, dosya içe aktarmayı desteklemeyen eski bir sürüm. Kapatıp güncellenmiş klasörden yeniden başlatın.',
    importStopped: 'Yükleme durduruldu · Orijinal metin panelindeki mesaja bakın'
  },
  ru: {
    serviceOutdated: 'Локальный сервис — старая версия без импорта файлов. Закройте его и запустите из обновлённой папки.',
    importStopped: 'Загрузка прервана · Проверьте сообщение в панели исходного текста'
  }
};

const contactLabels = {
  it: 'Telefoni, email e link',
  en: 'Phone, email and links',
  es: 'Teléfonos, correo y enlaces',
  de: 'Telefon, E-Mail und Links',
  fr: 'Téléphones, e-mails et liens',
  pt: 'Telefones, email e links',
  nl: 'Telefoon, e-mail en links',
  pl: 'Telefon, e-mail i linki',
  tr: 'Telefon, e-posta ve bağlantılar',
  ru: 'Телефоны, почта и ссылки'
};

const brandTranslations = {
  "it": {
    "madeBy": "Realizzata da",
    "rightsReserved": "Tutti i diritti riservati."
  },
  "en": {
    "madeBy": "Made by",
    "rightsReserved": "All rights reserved."
  },
  "es": {
    "madeBy": "Creada por",
    "rightsReserved": "Todos los derechos reservados."
  },
  "de": {
    "madeBy": "Entwickelt von",
    "rightsReserved": "Alle Rechte vorbehalten."
  },
  "fr": {
    "madeBy": "Créée par",
    "rightsReserved": "Tous droits réservés."
  },
  "pt": {
    "madeBy": "Desenvolvida por",
    "rightsReserved": "Todos os direitos reservados."
  },
  "nl": {
    "madeBy": "Gemaakt door",
    "rightsReserved": "Alle rechten voorbehouden."
  },
  "pl": {
    "madeBy": "Stworzona przez",
    "rightsReserved": "Wszelkie prawa zastrzeżone."
  },
  "tr": {
    "madeBy": "Geliştiren",
    "rightsReserved": "Tüm hakları saklıdır."
  },
  "ru": {
    "madeBy": "Разработано",
    "rightsReserved": "Все права защищены."
  }
};

const translations = Object.fromEntries(Object.entries(translationRows).map(([language, row]) => {
  if (row.length !== translationKeys.length) throw new Error(
    `Incomplete translation: ${language}`);
  return [language, {
    ...Object.fromEntries(translationKeys.map((key, i) => [key, row[i]])),
    ...appearanceTranslations[language],
    ...brandTranslations[language],
    ...uploadTranslations[language],
    ...importServiceTranslations[language],
    contacts: contactLabels[language]
  }];
}));
