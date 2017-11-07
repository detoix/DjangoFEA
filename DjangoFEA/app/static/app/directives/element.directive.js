(function () {
    'use strict';

    angular.module('djangofea')
        .directive('element', ElementDirective);

    function ElementDirective() {
        return {
            templateUrl: '/static/app/directives/element.html',
            restrict: 'A',
            replace: true,
            controller: ['$scope', '$http', function ($scope, $http) {
                var url = '/elements/' + $scope.element.id + '/';
                $scope.update = function () {
                    $http.put(url, $scope.element).then(
                        function () {
                            $scope.onload();
                        }
                    );
                };

                $scope.delete = function () {
                    $http.delete(url).then(
                        function () {
                            var elements = $scope.elements;
                            elements.splice(
                                elements.indexOf($scope.element),
                                1
                            );
                        }
                    );
                };

                $scope.modelOptions = {
                    debounce: 500
                }
            }]
        };
    }
})();