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
                    $http.put(url, $scope.node).then(
                        function () {
                            $scope.onload();
                        }
                    );
                };

                $scope.delete = function () {
                    $http.delete(url).then(
                        function () {
                            var nodes = $scope.nodes;
                            nodes.splice(
                                nodes.indexOf($scope.node),
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