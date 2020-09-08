var fs = require('fs'),
    included_files_ = {};

global.include = function(fileName) {
    // console.log('Loading file: ' + fileName);
    var ev = require(fileName);
    for (var prop in ev) {
        // console.log('Loading prop:' + prop);
        global[prop] = ev[prop];
    }
    included_files_[fileName] = true;
};

global.include_once = function(fileName) {
    if (!included_files_[fileName]) {
        include(fileName);
    }
};

global.include_folder_once = function(folder) {
    var file, fileName,
        files = fs.readdirSync(folder);

    var getFileName = function(str) {
        var splited = str.split('.');
        splited.pop();
        return splited.join('.');
    },

    getExtension = function(str) {
        var splited = str.split('.');
        return splited[splited.length - 1];
    };

    for (var i = 0; i < files.length; i++) {
        file = files[i];
        if (getExtension(file) === 'js') {
            fileName = getFileName(file);
            try {
                include_once(folder + '/' + file);
            } catch (err) {
                console.log(err);
            }
        }
    }
};
