(function () {
    'use strict';

    angular.module('djangofea')
        .directive('concentrated', ConcentratedLoadDirective);

    function ConcentratedLoadDirective() {
        return {
            templateUrl: '/static/app/directives/concentratedLoad.html',
            restrict: 'A',
            replace: true,
            controller: ['$scope', '$http', function ($scope, $http) {
                var url = '/concentrated-loads/' + $scope.concentratedLoad.id + '/';
                $scope.update = function () {
                    $http.put(url, $scope.concentratedLoad);
                };

                $scope.delete = function () {
                    $http.delete(url).then(
                        function () {
                            var concentratedLoads = $scope.concentratedLoads;
                            concentratedLoads.splice(
                                concentratedLoads.indexOf($scope.concentratedLoad),
                                1
                            );
                        }
                    );
                };

                $scope.modelOptions = {
                    debounce: 500
                };
            }]
        };
    }
})();