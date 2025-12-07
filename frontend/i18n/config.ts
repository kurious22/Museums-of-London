import { I18n } from 'i18n-js';
import * as Localization from 'expo-localization';
import en from '../translations/en.json';
import es from '../translations/es.json';
import fr from '../translations/fr.json';
import de from '../translations/de.json';
import zh from '../translations/zh.json';
import ja from '../translations/ja.json';
import ko from '../translations/ko.json';
import pt from '../translations/pt.json';
import it from '../translations/it.json';
import ru from '../translations/ru.json';

const i18n = new I18n({
  en,
  es,
  fr,
  de,
  zh,
  ja,
  ko,
  pt,
  it,
  ru,
});

// Set the locale once at the beginning of your app.
const deviceLocale = Localization.locale || Localization.getLocales()[0]?.languageCode || 'en';
i18n.locale = deviceLocale.split('-')[0];

// When a value is missing from a language it'll fall back to another language with the key present.
i18n.enableFallback = true;
i18n.defaultLocale = 'en';

export default i18n;
