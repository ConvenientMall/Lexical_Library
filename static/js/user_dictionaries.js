// This will be the object that will contain the Vue attributes
// and be used to initialize it.
let app = {};


// Given an empty app object, initializes it filling its attributes,
// creates a Vue instance, and then initializes the Vue instance.
let init = (app) => {

    // This is the Vue data.
    app.data = {
        add_mode: false,
        add_title: "",
        add_text: "",
        add_public: false,
        dictionaries: [],
        current_email: "",
        username: "",
    };

    app.enumerate = (a) => {
        // This adds an _idx field to each element of the array.
        let k = 0;
        a.map((e) => {e._idx = k++;});
        return a;
    };

    app.publish = function () {
        axios.post(add_dictionary_url,
            {
                adding_text: app.vue.add_text,
                adding_title: app.vue.add_title,
                adding_public: app.vue.add_public,

            }).then(function (response) {
            app.vue.dictionaries.push({
                id: response.data.id,
                title: app.vue.add_title,
                text: app.vue.add_text,
                public: app.vue.add_public,
                username: app.vue.username,
                created_by:app.vue.current_email,
            });
            app.reset_form();
            app.set_add_status(false);
            app.enumerate(app.vue.posts);
        });
    };

    app.reset_form = function () {
        app.vue.add_title = "";
        app.vue.add_text = "";
        app.vue.add_public = false;
    };
    
    app.delete_dictionary = function(row_idx) {
        if(confirm("Do you really want to delete?")){
        let id = app.vue.dictionaries[row_idx].id;
        axios.get(delete_dictionary_url, {params: {id: id}}).then(function (response) {
            for (let i = 0; i < app.vue.dictionaries.length; i++) {
                if (app.vue.dictionaries[i].id === id) {
                    app.vue.dictionaries.splice(i, 1);
                    app.enumerate(app.vue.dictionaries);
                    break;
                }
            }
        });
        }
    };


    app.set_add_status = function (new_status) {
        app.vue.add_mode = new_status;
    };

    app.get_email = function(p_email){
        return app.vue.current_email === p_email;
    };

    app.get_link = function(base,name,extra){
        // console.log(base)
        return base+"/"+encodeURIComponent(extra);
    }

    // This contains all the methods.
    app.methods = {
        get_link: app.get_link,
        get_email: app.get_email,
        reset_form : app.reset_form,
        enumerate:app.enumerate,
        set_add_status: app.set_add_status,
        publish: app.publish,
        delete_dictionary: app.delete_dictionary,

    };



    // This creates the Vue instance.
    app.vue = new Vue({
        el: "#vue-target",
        data: app.data,
        methods: app.methods
    });

    // And this initializes it.
    app.init = () => {
        // Put here any initialization code.
        // Typically this is a server GET call to load the data.
        axios.get(load_email_url).then(function (response) {
            app.vue.current_email = response.data.email;
            axios.get(load_personal_dictionaries_url).then(function (response) {
                let dictionaries_tmp = response.data.rows;
                app.enumerate(dictionaries_tmp);
                app.vue.dictionaries = dictionaries_tmp;
                });
            
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
