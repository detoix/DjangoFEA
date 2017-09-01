(function () {
    'use strict';

    angular.module('djangofea')
        .config(['$routeProvider', config])
        .run(['$http', run]);

    function config($routeProvider) {
        $routeProvider
            .when('/', {
                templateUrl: '/static/app/templates/index.html',
                controller: 'Controller',
            })
            .when('/about/', {
                templateUrl: '/static/app/templates/about.html',
                controller: 'Controller',
            })
            .when('/contact/', {
                templateUrl: '/static/app/templates/contact.html',
                controller: 'Controller',
            })
            .when('/login/', {
                templateUrl: '/static/app/templates/login.html',
                controller: 'Controller',
            })
            .otherwise('/');
    }

    function run($http) {
        $http.defaults.xsrfHeaderName = 'X-CSRFToken';
        $http.defaults.xsrfCookieName = 'csrftoken';
    }
})();