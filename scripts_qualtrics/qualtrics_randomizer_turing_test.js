Qualtrics.SurveyEngine.addOnload(function() {
    
    let posts = [];
    
    for(let i = 1; i <= 13; i++) {
        let mides = (i === 11) ? [8, 16, 30] : [8, 16];
        posts.push({ id: 'imm_' + i, topic: 'immigració', lengths: mides });
    }
    
    for(let i = 1; i <= 8; i++) {
        let mides = (i === 2) ? [8, 16, 30] : [8, 16];
        posts.push({ id: 'clim_' + i, topic: 'clima', lengths: mides });
    }

    function getRandomSample(array, size) {
        let shuffled = array.slice().sort(() => 0.5 - Math.random());
        return shuffled.slice(0, size);
    }

    function isValidMix(selection) {
        let hasImm = selection.some(p => p.topic === 'immigració');
        let hasClim = selection.some(p => p.topic === 'clima');
        return hasImm && hasClim;
    }

    let validSelection = false;
    let finalSelection = [];

    while(!validSelection) {
        
        let realSample = getRandomSample(posts, 3);
        let fakeSample = getRandomSample(posts, 3);
        
        let realPosts = realSample.map(p => {
            let longitudTrobada = p.lengths[Math.floor(Math.random() * p.lengths.length)];
            return { type: 'reals', id: p.id, topic: p.topic, length: longitudTrobada };
        });
        
        let fakePosts = fakeSample.map(p => {
            let longitudTrobada = p.lengths[Math.floor(Math.random() * p.lengths.length)];
            return { type: 'ficticis', id: p.id, topic: p.topic, length: longitudTrobada };
        });
        
        finalSelection = realPosts.concat(fakePosts);
        
        if(isValidMix(finalSelection)) {
            validSelection = true;
        }
    }
    
    finalSelection.sort(() => 0.5 - Math.random());
    
    let baseUrl = "https://alexcasadevall.github.io/turing-test-what-if";
    
    finalSelection.forEach((post, index) => {
        let postNum = index + 1; 
        
        let fileUrl = baseUrl + "/" + post.type + "/" + post.length + "/" + post.id + ".json";
        
        Qualtrics.SurveyEngine.setEmbeddedData("URL_Post_" + postNum, fileUrl);
        Qualtrics.SurveyEngine.setEmbeddedData("Categoria_" + postNum, post.type);
        Qualtrics.SurveyEngine.setEmbeddedData("Tema_" + postNum, post.topic);
        Qualtrics.SurveyEngine.setEmbeddedData("Mida_" + postNum, post.length);
        Qualtrics.SurveyEngine.setEmbeddedData("ID_" + postNum, post.id);
    });
});