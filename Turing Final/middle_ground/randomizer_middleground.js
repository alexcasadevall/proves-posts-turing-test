Qualtrics.SurveyEngine.addOnload(function() {

    var temaEscollit = (Math.random() < 0.5) ? 'clima' : 'immigracio';
    
    Qualtrics.SurveyEngine.setJSEmbeddedData('MG_Tema', temaEscollit);

    var tractaments = ['20', '50', '80'];
    tractaments.sort(function() { return 0.5 - Math.random(); });

    Qualtrics.SurveyEngine.setJSEmbeddedData('MG_Forum_1_Tractament', tractaments[0]);
    Qualtrics.SurveyEngine.setJSEmbeddedData('MG_Forum_2_Tractament', tractaments[1]);
    Qualtrics.SurveyEngine.setJSEmbeddedData('MG_Forum_3_Tractament', tractaments[2]);

    var baseUrl = "https://alexcasadevall.github.io/turing-test-what-if/middle_ground/";
    
    Qualtrics.SurveyEngine.setJSEmbeddedData('MG_URL_1', baseUrl + temaEscollit + "/" + tractaments[0] + ".json");
    Qualtrics.SurveyEngine.setJSEmbeddedData('MG_URL_2', baseUrl + temaEscollit + "/" + tractaments[1] + ".json");
    Qualtrics.SurveyEngine.setJSEmbeddedData('MG_URL_3', baseUrl + temaEscollit + "/" + tractaments[2] + ".json");

    console.log("MIDDLE GROUND BRAIN EXECUTAT:");
    console.log("Tema assignat:", temaEscollit);
    console.log("Ordre d'aparició:", tractaments);
});