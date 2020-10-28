## Install

```bash
$ npm install --save papago
```

## Usages

#### Prerequisite

You have to configure environment variables like below to test

```
export CLIENT_ID='Your application's client id'
export CLIENT_SECRET='Your application's client secret'
```

#### APIs

Default values are translated into English

```javascript
import Translator from 'papago';

translator = new Translator(process.env.CLIENT_ID, process.env.CLIENT_SECRET);
translator.translate('안녕하세요')
.then(result => {
  console.log(result.text); // Hello.
})
.catch(err => {
    console.log(err.code);
});
```

You can select the target language as shown below.

```javascript
import Translator from 'papago';

translator = new Translator(process.env.CLIENT_ID, process.env.CLIENT_SECRET);
translator.translate('안녕하세요', 'ko', 'es')
.then(result => {
  console.log(result.text); // Hola
})
.catch(err => {
  console.log(err.code);
});
```

#### Languages Code

The Papago API supports the following language codes:

Code | Desc 
--|--
ko | Korean
en | English
ja | Japanese
zh-CN | Chinese
es | Spainish
th | Thai
fr | French
vi | Vietnamese
id | Hindi

## License

```
MIT
```