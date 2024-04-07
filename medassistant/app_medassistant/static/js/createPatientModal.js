import "./select2adapters.js";
import { showError } from "./main.js";

export function openCreatePatientModal() {
    $('#patientname').select2('close');
    $('#createPatientModal').modal('show');
  
    $('#birthdate').datepicker({
        format: "dd.mm.yyyy"
    });
  
    var omsInput = document.querySelector('.oms-input');
    var omsParts = document.querySelectorAll('.oms-part');
  
    var oms1 = document.getElementById('oms1');
    var oms2 = document.getElementById('oms2');
    var oms3 = document.getElementById('oms3');
    var oms4 = document.getElementById('oms4');
  
    omsInput.addEventListener('click', function(event) {
        if (event.target === omsInput) {   
            for (var i = omsParts.length - 1; i >= 0; i--) {
                if (omsParts[i].value.length > 0 || i === 0) {
                    if (omsParts[i].value.length < 3) {
                        omsParts[i].focus();
                    } else {
                        omsParts[i + 1].focus();
                    }
                    break;
                }
            }
        }
    });
  
    omsParts.forEach(function(input, index) {
        input.addEventListener('input', function() {
            var value = input.value;
        
            if (value.length === input.maxLength && index < omsParts.length - 1) {
                omsParts[index + 1].focus();
            }
        });
  
        input.addEventListener('keydown', function(event) {
            if (event.key === 'Backspace' && input.value.length === 0 && index > 0) {
                omsParts[index - 1].focus();
            } else if (event.key === 'ArrowRight' && input.selectionStart === input.value.length && index < omsParts.length - 1) {
                omsParts[index + 1].focus();
                setTimeout(function () {
                    omsParts[index + 1].setSelectionRange(1, 1);
                }, 0);
                event.preventDefault();
            } else if (event.key === 'ArrowLeft' && input.selectionStart <= 1 && index > 0) {
                omsParts[index - 1].focus();
                setTimeout(function () {
                    const newSelection = omsParts[index - 1].value.length;
                    omsParts[index - 1].setSelectionRange(newSelection, newSelection);
                }, 0);
                event.preventDefault();
            }
        });
  
        input.addEventListener('paste', function (event) {
            event.preventDefault();
        });
    });
  
    function createPatientSubmitHandler (event) {
        event.preventDefault();
        
        var formData = new FormData();

        var selectedSex = $("#sex").select2('data')[0].id;
        
        formData.append("fullname", $("#fullname").val());
        formData.append("birthdate", $("#birthdate").val());
        formData.append("oms", `${oms1.value}-${oms2.value}-${oms3.value} ${oms4.value}`);
        formData.append("sex", selectedSex);
        
        var imageFile = $('#file-input')[0].files[0];
        if (imageFile) {
            formData.append("image", imageFile);
        }

        $.ajax({
            url: '/create_patient',
            method: 'POST',
            data: formData,
            contentType: false,
            processData: false,
            success: function(response) {
                var $select = $('#patientname');

                $select.select2('trigger', 'select', { data: response });
        
                $('#createPatientModal').modal('hide');
            },
            error: function(xhr, status, error) {
                console.error('Ошибка при создании нового пациента: ' + error);
                var errorMessage = "Произошла ошибка при создании нового пациента. Пожалуйста, попробуйте еще раз.";
                showError(errorMessage);
            }
        });
    };

    $("#create-patient-form").on('submit', createPatientSubmitHandler);
  
    $('#createPatientModal').on('hidden.bs.modal', function() {
        var form = document.getElementById('create-patient-form');
        
        if (form) {
            form.reset();
        }

        $("#create-patient-form").off('submit', createPatientSubmitHandler);

        removeImage();
    });
  
    oms1.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');
    });
    
    oms2.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');
    });
    
    oms3.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');
    });
    
    oms4.addEventListener('input', function() {
        this.value = this.value.replace(/\D/g, '');
    });
}

$('#sex').select2({
    theme: 'bootstrap-5',
    dropdownAdapter: $.fn.select2.amd.require("SexDropdownAdapter"),
    closeOnSelect: true,
    language: {
        errorLoading: () => 'Невозможно загрузить пол'
    }
});

function handleDragOver(event) {
    event.preventDefault();
    event.dataTransfer.dropEffect = 'copy';
}
window.handleDragOver = handleDragOver;

function handleDragEnter(event) {
    var uploadText = document.getElementById('image-upload');
    uploadText.style.background = '#dcdcdc';
}
window.handleDragEnter = handleDragEnter;

function handleDragLeave(event) {
    var uploadText = document.getElementById('image-upload');
    uploadText.style.background = 'var(--background-color)';
}
window.handleDragLeave = handleDragLeave;

function handleDrop(event) {
    event.preventDefault();
    var uploadText = document.getElementById('image-upload');
    uploadText.style.background = 'var(--background-color)';
    
    var file = event.dataTransfer.files[0];
    displayImage(file);
}
window.handleDrop = handleDrop;

var isDeletingImage = false;

function handleFileClick(event) {
    if (isDeletingImage) {
        isDeletingImage = false;
        event.preventDefault();
    }
}
window.handleFileClick = handleFileClick;

function handleFileSelect(event) {
    var file = event.target.files[0];
    displayImage(file);
}
window.handleFileSelect = handleFileSelect;

function displayImage(file) {
    if (file && file.type.match('image.*')) {
        var reader = new FileReader();
        reader.onload = function(e) {
            var img = new Image();
            img.src = e.target.result;
            img.onload = function() {
                var canvas = document.createElement('canvas');
                var ctx = canvas.getContext('2d');
                const cropSize = 256;
                canvas.width = cropSize;
                canvas.height = cropSize;
                ctx.drawImage(img, 0, 0, 256, 256);

                var thumbnail = document.getElementById('thumbnail');
                thumbnail.src = canvas.toDataURL('image/png');

                var uploadText = document.getElementById('image-upload-block');
                uploadText.style.display = 'none';

                var thumbnailContainer = document.getElementById('thumbnail-container');
                thumbnailContainer.style.display = 'flex';

                document.getElementById('delete-icon').addEventListener('click', function (event) {
                    event.stopPropagation();
                    removeImage();
                });

                var imageData = ctx.getImageData(0, 0, cropSize, cropSize);
                var data = imageData.data;
                var totalBrightness = 0;

                for (var i = 0; i < data.length; i += 4) {
                    var brightness = Math.min((299 * data[i] + 587 * data[i + 1] + 114 * data[i + 2]) / (Math.max(1, data[i + 3]) / 255) / 1000, 255);
                    if (data[i + 3] < 128) brightness = 255;
                    totalBrightness += brightness;
                }

                var averageBrightness = totalBrightness / (cropSize * cropSize);
                
                var isLightColor = averageBrightness > 128;
                var deleteIcon = document.getElementById('delete-icon');
                deleteIcon.style.color = isLightColor ? 'var(--primary-color)' : 'var(--background-color)';
            };
        };
        reader.readAsDataURL(file);
    }
}
window.displayImage = displayImage;

function removeImage() {
    isDeletingImage = true;

    var thumbnail = document.getElementById('thumbnail');
    var uploadText = document.getElementById('image-upload-block');
    uploadText.style.display = 'block';

    var thumbnailContainer = document.getElementById('thumbnail-container');
    thumbnailContainer.style.display = 'none';

    var canvas = document.createElement('canvas');
    var ctx = canvas.getContext('2d');
    canvas.width = 256;
    canvas.height = 256;
    ctx.clearRect(0, 0, canvas.width, canvas.height);

    thumbnail.src = canvas.toDataURL('image/png');
}

window.openCreatePatientModal = openCreatePatientModal;
