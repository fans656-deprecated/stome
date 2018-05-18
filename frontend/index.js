const js_md5 = md5;

$(function() {
  // history backward / forward
  window.onpopstate = function({state}) {
    list_directory(state.path);
  };
  window.history.replaceState({path: get_current_path()}, '', '');

  // list directory initially
  list_directory(get_current_path());

  // when click "Upload file", trigger files selection
  $('#upload').on('click', function() {
    $('#file-input').click();
  });

  // when files are selected, do upload
  $('#file-input').on('change', function() {
    var fileinput = $(this);
    var files = fileinput[0].files;
    if (files.length === 1) {
      upload_file(files[0], $('#name').val());
    } else {
      upload_files(files);
    }
    fileinput.val(null);
  });

  // type in #name and press enter to create directory or upload file
  // e.g.
  //     foo/bar/ to create direcotry
  //     img/girl.jpg to upload file
  $('#name').on('keypress', function(ev) {
    if (ev.keyCode === 13) {
      var text = $('#name').val();
      if (text.length && text.endsWith('/')) {
          console.log('create direcotry');
      } else {
        $('#upload').click();
      }
    }
  });
});

function get_current_path() {
  return window.location.pathname;
}

function list_directory(path) {
  $.get({
    url: origin + path,
    success: function(data) {
      console.log(data);
      populate_file_list(path, JSON.parse(data));
    }
  });
}

function populate_file_list(path, data) {
  var file_list = $('#file-list');
  file_list.empty();
  if (path !== '/') {
    file_list.append(make_directory_item({
      name: '..',
      path: path.substring(0, path.lastIndexOf('/')) || '/'
    }));
  }
  data['dirs'].forEach(dir => {
    file_list.append(make_directory_item(dir));
  });
  data['files'].forEach(file => {
    file_list.append(make_file_item(file));
  });
}

function navigate_to(path) {
  window.history.pushState({'listdir': true, 'path': path}, '', get_origin() + path);
  list_directory(path);
}

function make_directory_item(node) {
  let name = node.name;
  if (name !== '..') {
    name += '/';
  }
  var a = $('<a>' + name + '</a>');
  a.addClass('dir')
    .attr('href', get_origin() + node.path)
    .attr('data-path', node.path);
  a.on('click', function(ev) {
    ev.preventDefault();
    navigate_to($(this).attr('data-path'));
  });
  return $('<li>').append(a);
}

function make_file_item(file) {
  var a = $('<a>' + file.name + '</a>');
  a.addClass('file')
    .attr('href', get_origin() + file.path)
    .attr('data-path', file.path);
  return $('<li>').append(a);
}

function get_origin() {
  return window.location.origin;
}

function upload_files(files) {
  for (var i = 0; i < files.length; ++i) {
    var file = files.item(i);
    upload_file(file);
  };
}

function upload_file(file, path) {
  if (path) {
    $('#name').val(null);
  }
  path = path || file.name;
  if (!path.startsWith('/')) {
    let cur = get_current_path();
    if (!cur.endsWith('/')) {
      cur += '/';
    }
    path = cur + path;
  }
  return;
  if (file.size < 1 * MB) {
    upload_as_a_whole(file, path);
  } else {
    upload_as_parts(file, path);
  }
}

function upload_as_a_whole(file, fpath) {
  var form = new FormData();
  form.append('meta', {
  });
  form.append('data', file);
  $.ajax({
    type: 'PUT',
    url: origin + '/' + fpath,
    data: form,
    contentType: false,
    processData: false,
    success: function() {
      list_directory(get_current_path());
    }
  });
}

function upload_as_parts(file, fpath) {
  // calculate file md5
  var m = js_md5.create();
  var uploaded_size = 0;
  var total_size = file.size;

  var uploading_file = $('<li>' + file.name + '</li>');
  uploading_file.addClass('uploading-file');
  uploading_file.attr('id', fpath.replace('.', '_'));
  uploading_file.append($('<span class="progress">Preparing...</span>'));
  $('#upload-list').append(uploading_file);

  chunked_read(file, (data, pos, len) => {
    m.update(data);
  }, () => {
    // md5 calculated
    var md5 = m.hex();
    chunked_read(file, (data, pos, len) => {
      var file = new File([data], '');
      var form = new FormData();
      form.append('md5', md5);
      form.append('pos', pos);
      form.append('part-size', len);
      form.append('data', file);
      form.append('mimetype', file.type);
      $.ajax({
        type: 'PUT',
        url: origin + '/' + fpath,
        data: form,
        contentType: false,
        processData: false,
        success: function(data) {
          uploaded_size += len;
          var progress = (uploaded_size / total_size * 100).toFixed(2) + '%';
          $('#upload-list #' + fpath.replace('.', '_') + ' .progress').text(progress);
          console.log(progress);
          if (uploaded_size == total_size) {
            list_directory(get_current_path());
          }
        }
      });
    });
  });
}

function chunked_read(file, callback, final_callback=() => {}, pos=0, len=CHUNK_SIZE) {
  var slice = file.slice(pos, pos + len);
  var reader = new FileReader();
  reader.onload = function() {
    callback(reader.result, pos, slice.size);
    if (pos + slice.size < file.size) {
      chunked_read(file, callback, final_callback, pos + slice.size, CHUNK_SIZE);
    } else {
      final_callback();
    }
  }
  reader.readAsArrayBuffer(slice);
}
