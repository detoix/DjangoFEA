(function () {
    'use strict';

    angular.module('djangofea')
        .directive('node', NodeDirective);

    function NodeDirective() {
        return {
            templateUrl: '/static/app/directives/node.html',
            restrict: 'A',
            replace: true,
            controller: ['$scope', '$http', function ($scope, $http) {
                var url = '/nodes/' + $scope.node.id + '/';
                $scope.update = function () {
                    $http.put(url, $scope.node);
                };

                $scope.modelOptions = {
                    debounce: 500
                }
            }]
        };
    }
})();