(function () {
    'use strict';

    angular.module('djangofea')
        .directive('section', SectionDirective);

    function SectionDirective() {
        return {
            templateUrl: '/static/app/directives/section.html',
            restrict: 'A',
            replace: true,
            controller: ['$scope', '$http', function ($scope, $http) {
                var url = '/sections/' + $scope.section.id + '/';
                $scope.update = function () {
                    $http.put(url, $scope.section);
                };

                $scope.delete = function () {
                    $http.delete(url).then(
                        function () {
                            var sections = $scope.sections;
                            sections.splice(
                                sections.indexOf($scope.section),
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