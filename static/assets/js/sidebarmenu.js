$(function () {
  "use strict";
  
  // Pega só o caminho atual, ex: /pedidos/
  var currentPath = window.location.pathname;

  // Seleciona o link correspondente
  var element = $("ul#sidebarnav a").filter(function () {
    return this.pathname === currentPath;
  });

  // Marca o item e abre o menu pai se necessário
  element.each(function () {
    $(this).addClass("active");

    $(this).parentsUntil(".sidebar-nav").each(function () {
      if ($(this).is("li") && $(this).children("a").length !== 0) {
        $(this).children("a").addClass("active");
        $(this).addClass("selected");
      } else if (!$(this).is("ul") && $(this).children("a").length === 0) {
        $(this).addClass("selected");
      } else if ($(this).is("ul")) {
        $(this).addClass("in");
      }
    });
  });

  // Controle de clique no menu
  $("#sidebarnav a").on("click", function (e) {
    if (!$(this).hasClass("active")) {
      $("ul", $(this).parents("ul:first")).removeClass("in");
      $("a", $(this).parents("ul:first")).removeClass("active");
      $(this).next("ul").addClass("in");
      $(this).addClass("active");
    } else {
      $(this).removeClass("active");
      $(this).parents("ul:first").removeClass("active");
      $(this).next("ul").removeClass("in");
    }
  });

  $("#sidebarnav >li >a.has-arrow").on("click", function (e) {
    e.preventDefault();
  });
});
