// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};

// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        search_Query:"",
        user_mode: false,
        edit_mode: false,
        add_mode: false,
        dictionary_id: "",
        add_word: "",
        add_position: "",
        add_english: "",
        add_definition: "",
        add_other: "",
        edit_title: "",
        edit_text: "",
        selected: "Default",
        edit_public: false,
        display_words: [],
        words: [],
        alphwords: [],
        dictionaries: [],
        current_email: "",
        current_dictionary: "",
        username: "",

    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.publish = function () {
        axios.post(add_word_url,
            {
                adding_word: app.vue.add_word,
                adding_position: app.vue.add_position,
                adding_english: app.vue.add_english,
                adding_definition: app.vue.add_definition,
                adding_other: app.vue.add_other,
                adding_dictionary_id: app.vue.dictionary_id,

            }).then(function (response) {
            app.vue.words.push({
                id: response.data.id,
                dictionary: app.vue.dictionary_id,
                word: app.vue.add_word,
                position: app.vue.add_position,
                english: app.vue.add_english,
                definition: app.vue.add_definition,
                other:app.vue.add_other,
            });
            app.reset_form();
            app.set_add_status(false);
            app.enumerate(app.vue.posts);
        });
    };

    app.edit = function () {
        axios.post(edit_dictionary_url,
            {
                edit_id: app.vue.dictionary_id,
                edit_text: app.vue.edit_text,
                edit_title: app.vue.edit_title,
                edit_public: app.vue.edit_public,

            }).then(function (response){

            app.reset_form();
            app.set_edit_status(false);
            location.reload();
        });
    };

    app.reset_form = function () {
        app.vue.add_mode = false;
        app.vue.add_word = "";
        app.vue.add_position = "";
        app.vue.add_english = "";
        app.vue.add_definition = "";
        app.vue.add_other = "";
        app.vue.edit_title= "";
        app.vue.edit_text= "";
        app.vue.edit_public= false;
    };


    app.set_add_status = function (new_status) {
        app.vue.add_mode = new_status;
    };

    app.set_edit_status = function (new_status) {
        app.vue.edit_mode = new_status;
        if(app.vue.edit_mode === "Default"){
        
        }
        else if(app.vue.edit_mode === "Alphabetical"){
        
        }
    };

    app.set_alpha_status = function(new_status){
        app.vue.alpha_status = new_status;

    }

    app.get_email = function(p_email){
        return app.vue.current_email === p_email;
    };

    app.get_link = function(base,extra){
        // console.log(base)
        return base+"/"+encodeURIComponent(extra)
    }

    app.set_dictionary_filter = function (dictionary_id) {
        app.data.dictionary_id = dictionary_id;
    };


    app.set_current_dictionary = function (dictionary_id){
        let dictionaries = app.data.dictionaries;
        for (let i = 0; i < dictionaries.length; i++){
            let dictionary = dictionaries[i];
            if(dictionary.id == dictionary_id){
                app.data.current_dictionary = dictionary
                if(app.data.current_dictionary.created_by == app.data.current_email){
                    app.data.user_mode = true;
                }
                break;
            }
        }
    }

    app.set_user_mode = function(dictionary_id){
        let user_mode = true;
    }


    app.delete_word = function(row_idx) {
        let id = app.vue.words[row_idx].id;
        axios.get(delete_word_url, {params: {id: id}}).then(function (response) {
            for (let i = 0; i < app.vue.words.length; i++) {
                if (app.vue.words[i].id === id) {
                    app.vue.words.splice(i, 1);
                    app.enumerate(app.vue.words);
                    break;
                }
            }
        });
    };


    // This contains all the methods.
    app.methods = {
        filteredWords: app.filteredWords,
        set_alpha_status: app.set_alpha_status,
        set_edit_status: app.set_edit_status,
        edit: app.edit,
        set_user_mode: app.set_user_mode,
        get_link: app.get_link,
        get_email: app.get_email,
        reset_form : app.reset_form,
        enumerate:app.enumerate,
        set_add_status: app.set_add_status,
        publish: app.publish,
        set_dictionary_filter: app.set_dictionary_filter,
        delete_word: app.delete_word,
        set_current_dictionary: app.set_current_dictionary,

    };



    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });


    function checkDictionary(words) {
        return words.dictionary == app.data.dictionary_id;
    }

    app.init = () => {
        axios.get(load_email_url).then(function (response) {
            app.vue.current_email = response.data.email;
            axios.get(load_dictionaries_url).then(function (response) {
                let dictionaries_tmp = response.data.rows;
                app.enumerate(dictionaries_tmp);
                app.vue.dictionaries = dictionaries_tmp;
                });
            
            });

            axios.get(load_words_url).then(function (response) {
                let words_temp = response.data.rows.filter(checkDictionary);
                app.enumerate(words_temp);
                words_temp.sort((a, b) => a.word.localeCompare(b.word))
                app.vue.words = words_temp;
                app.vue.display_words = app.vue.words
            });

            axios.get(load_username_url).then(function (response) {
                app.vue.username = response.data.username;
                
            });
    };



    // Call to the initializer.
    app.init();
};


  
// This takes the (empty) app object, and initializes it,
// putting all the code i
init(app);