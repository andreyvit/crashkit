jQuery(function($) {
  var selectedKeys = [];
  
  function selectionUpdated() {
    var keys = [];
    $('.bug-row.selected').each(function() {
      keys.push($('.bug-key', this).val());
    });
    var len = keys.length;
    var suffix = (len == 0 ? "" : " (" + len + ")")
    $('.mass-reopen').html("Reopen" + suffix);
    $('.mass-close').html("Close" + suffix);
    $('.mass-ignore').html("Ignore" + suffix);
    selectedKeys = keys;
  }
  
  function massEdit(action) {
    if (selectedKeys.length == 0) {
      alert('Please select one or more bugs first.');
      return;
    }
    $('#mass-edit-action').val(action);
    $('#mass-edit-bugs').val(selectedKeys.join("\n"));
    $('#mass-edit-form').submit();
  }
  
  $('.row-selector').click(function() {
    $(this).closest('tr').toggleClass('selected')
      .next().toggleClass('selected');
    selectionUpdated();
  });
  $('.select-all').click(function() {
    $('.bug-row').addClass('selected').next().addClass('selected')
      .end().find('.row-selector').attr('checked', 'checked');
    selectionUpdated();
  });
  $('.select-none').click(function() {
    $('.bug-row').removeClass('selected').next().removeClass('selected')
      .end().find('.row-selector').removeAttr('checked');
    selectionUpdated();
  });
  
  $('.mass-reopen').click(function(){ massEdit('reopen'); });
  $('.mass-close').click(function(){ massEdit('close'); });
  $('.mass-ignore').click(function(){ massEdit('ignore'); });
  
  $('.row-selector').each(function() {
    if ($(this).val())
      $(this).closest('tr').addClass('selected').next().addClass('selected');
  });
  selectionUpdated();
  
});