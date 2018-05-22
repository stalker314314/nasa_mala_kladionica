
$( "#next-step-btn" ).bind( "click", function(event) {
  event.stopImmediatePropagation();
  scroll( this, 1 );
});

$(document).on( 'scroll', function(){
  console.log('Event Fired');
});

$(window).scroll(function() {
  var hT = $('#plans').offset().top,
      hH = $('#plans').outerHeight(),
      wH = $(window).height(),
      wS = $(this).scrollTop();
  if (wS > (hT+hH-wH)){
    $( "#intro-disclaimer" ).css('opacity', '.7');
    $(window).off('scroll')
  }
});

function scroll( id, multiplier, extra=0 ) {
  $( "html, body" ).animate({ scrollTop: $( window ).height() * multiplier + extra + "px" }, 800);
  // $( focused_nav_item ).removeClass( "nav-item-active" );
  // $( id ).addClass( "nav-item-active" );
  focused_nav_item = id;
}
