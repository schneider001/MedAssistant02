import { showError } from "./main.js";
import { setupCSRF } from "./csrf.js";

setupCSRF();

let requestId;
const webSocket = new WebSocket('ws://' + window.location.host + '/ws');


window.addEventListener('beforeunload', function() {
    webSocket.close();
});

webSocket.onmessage = function(event) {
    const data = JSON.parse(event.data);
    switch(data.type) {
        case 'recieve_error':
            showError('Произошла ошибка: ' + data.message);
            break;
        case 'disconnect_error':
            showError('Произошла ошибка при отключении от сервера: ' + data.message);
            break;
        case 'join_room_error':
            showError('Произошла ошибка при подключении к комнате: ' + data.message);
            break;
        case 'leave_room_error':
            showError('Произошла ошибка при отключении от комнаты: ' + data.message);
            break;
        case 'add_comment_error':
            showError('Произошла ошибка при создании комментария: ' + data.message);
            break;
        case 'group_except_send_error':
            showError('Произошла ошибка: ' + data.message);
            break;
        case 'edit_comment_error':
            showError('Произошла ошибка при редактировании комментария: ' + data.message);
            break;
        case 'delete_comment_error':
            showError('Произошла ошибка при удалении комментария: ' + data.message);
            break;
        case 'added_comment':
            addCommentElement(data.comment);
            break;
        case 'self_added_comment':
            data.comment.editable = true;
            addCommentElement(data.comment);
            break;
        case 'edited_comment':
            editCommentElement(data.comment);
            break;
        case 'self_edited_comment':
            data.comment.editable = true;
            editCommentElement(data.comment);
            break;
        case 'deleted_comment':
            const elementToRemove = $(`#comment-${data.comment.id}`);
            if (elementToRemove.length > 0) {
                elementToRemove.remove();
            }
            const addCommentBlock = $('#add-comment');
            if (!addCommentBlock.length && elementToRemove.hasClass("editable-comment")) {
                createCommentInputBlock(data.comment.doctor);
            }
            break;
        default:
            console.log('Received unknown message:', data);
    }
};

webSocket.onerror = function() {
    showError('Произошла ошибка при обмене данными с сервером.');
};

webSocket.onclose = function() {
    showError('Соединение с сервером закрыто.');
};

export function openRequestInfoModal(mode, data) {
           
    const loadSection = document.getElementById('request-load-section');
    const dataSection = document.getElementById('request-data-section');

    loadSection.style.display = 'block';
    dataSection.style.display = 'none';

    $.ajax({
        url: mode === 'by_id' ? '/get_request_info_by_id' : '/get_request_info',
        method: 'POST',
        contentType: 'application/json',
        data: JSON.stringify(data),
        success: function(response) {
            requestId = response.id;
            webSocket.send(JSON.stringify({ action: 'join_room', room_id: response.id }));
            loadSection.style.display = 'none';
            dataSection.style.display = 'block';
            loadRequestInfoModal(response)
        },
        error: function(xhr, status, error) {
            console.error('Ошибка при получении информации о запросе: ' + error);
            var errorMessage = "Произошла ошибка при получении информации о запросе на сервере. Пожалуйста, попробуйте еще раз.";
            showError(errorMessage);
        }
    });
    
    requestId = data.request_id;
    $('#requestModal').modal('show');
}

$('#requestModal').on('hidden.bs.modal', function() {
    webSocket.send(JSON.stringify({ action: 'leave_room', room_id: requestId }));
    requestId = undefined;
});

function loadRequestInfoModal(response) {
    const $infoContainer = $('<div>', { class: 'container-fluid my-2 py-2' });

    const $patientInfo = $('<div>', { class: 'info-item' });
    $patientInfo.append($('<span>', { class: 'info-label' }).text('Имя пациента: '));
    $patientInfo.append($('<span>', { class: 'info-value', id: 'name' }).text(response.patient_name));

    const $symptomsInfo = $('<div>', { class: 'info-item' });
    $symptomsInfo.append($('<span>', { class: 'info-label' }).text('Симптомы: '));
    $symptomsInfo.append($('<span>', { class: 'info-value', id: 'symptoms' }).text(response.symptoms.join(', ')));

    const $diagnosisInfo = $('<div>', { class: 'info-item' });
    $diagnosisInfo.append($('<span>', { class: 'info-label' }).text('Предсказанный диагноз: '));
    $diagnosisInfo.append($('<span>', { class: 'info-value', id: 'diagnosis' }).text(response.diagnosis));

    $infoContainer.append($patientInfo, $symptomsInfo, $diagnosisInfo);

    const $commentsContainer = $('<div>', { class: 'container-fluid my-2 py-2' });
    const $commentsCard = $('<div>', { class: 'card comments-block-card' });
    const $commentsCardBody = $('<div>', { class: 'card-body p-4' });

    const $commentsTitle = $('<h4>', { class: 'text-center mb-2 pb-2', style: 'font-weight: bold' }).text('Комментарии врачей');

    const $comments = $('<div>', { class: 'row', id: 'comments-container' });

    response.doctor_comments.forEach(function(comment) {
        $comments.append(generateCommentElement(comment));
    });

    $commentsCardBody.append($comments);
    $commentsCard.append($commentsCardBody);
    $commentsContainer.append($commentsTitle, $commentsCard);

    const requestDataSection = $('#request-data-section');
    requestDataSection.empty().append($infoContainer, $commentsContainer);

    const hasEditableComment = response.doctor_comments.some(comment => comment.editable === 1);

    if (!hasEditableComment) {
        createCommentInputBlock(response.doctor);
    }
}

function createCommentBlock(id, doctor, comment, time, editable = false) {
    const $container1 = $('<div>', { class: 'container mb-3' });
    const $rowDoctorAndTime = $('<div>', { class: 'row g-3' });
    const $rowComment = $('<div>', { class: 'row g-3' });
    
    const $doctorName = $('<h6>', { class: 'col-8 text-primary fw-bold mb-0', text: doctor });
    const $timeElement = $('<p>', { class: 'col-4 mb-0 start', text: time });
    const $commentText = $('<span>', { class: 'text-dark', text: comment, style: 'font-weight: bold;' });
    
    $rowDoctorAndTime.append($doctorName, $timeElement);
    $rowComment.append($commentText);
    $container1.append($rowDoctorAndTime, $rowComment);
    
    let $container2;
    if (editable) {
        $container2 = $('<div>', { class: 'd-flex justify-content-between align-items-center' });
        const $deleteLink = $('<a>', { class: 'link-grey', text: 'Удалить', role: 'button', click: function() { deleteComment(id); } });
        const $editLink = $('<a>', { class: 'link-grey', text: 'Изменить', role: 'button', click: function() { editComment(id, doctor, comment, time); } });
        $container2.append($('<p>', { class: 'small mb-0', style: 'color: #aaa;' }).append($deleteLink, ' • ', $editLink));
    }

    return { container1: $container1, container2: $container2 };
}

function generateCommentElement(comment) {
    const $div = $('<div>', { class: 'card mb-3 comment-card', id: `comment-${comment.id}` });

    if (comment.editable) {
        $div.addClass("editable-comment");
    }

    const $cardBody = $('<div>', { class: 'card-body' });
    const $dFlexStart = $('<div>', { class: 'd-flex flex-start' });
    const $avatar = $('<img>', {
        class: 'rounded-circle shadow-1-strong me-3',
        src: '/static/images/default-avatar.png',
        alt: 'avatar',
        width: '64',
        height: '64'
    });
    const $flexContainer = $('<div>', { class: 'flex-grow-1 flex-shrink-1' });

    const $commentContent = $('<div>');

    if (comment.editable) {
        $commentContent.addClass("editable-comment-content");
    }

    const $commentBlock = createCommentBlock(comment.id, comment.doctor, comment.comment, comment.time, comment.editable);
    $commentContent.append($commentBlock.container1);
    if ($commentBlock.container2) {
        $commentContent.append($commentBlock.container2);
    }

    $flexContainer.append($commentContent);
    $dFlexStart.append($avatar, $flexContainer);
    $cardBody.append($dFlexStart);
    $div.append($cardBody);

    return $div;
}

function editComment(id, doctor, comment, time) {
    const commentBlock = $(`#comment-${id}`);
    const commentSection = commentBlock.find(".editable-comment-content");
    
    const $header = $('<div>').addClass('d-flex justify-content-between align-items-center mb-3');
    const $title = $('<h6>').addClass('text-primary fw-bold mb-0').text(doctor);
    const $time = $('<p>').addClass('mb-0').text(time);
    
    const $textareaWrapper = $('<div>').addClass('mb-4 position-relative');
    const $textarea = $('<textarea>').attr('placeholder', 'Введите ваш комментарий здесь').attr('rows', 4).addClass('form-control').attr('id', 'comment-textarea').text(comment);
    const $invalidTooltip = $('<div>').addClass('invalid-tooltip').text('Комментарий не должен быть пустым');
    
    const $buttonWrapper = $('<div>').addClass('d-flex justify-content-between align-items-center mt-3');
    const $smallText = $('<p>').addClass('small').css('color', '#aaa');
    const $saveButton = $('<button>').addClass('btn btn-theme text-end mx-1').text('Сохранить').on('click', function() {
        saveComment(id);
    });
    const $cancelButton = $('<button>').addClass('btn text-end mx-1').text('Отменить').on('click', function() {
        cancelEditComment(id, doctor, comment, time);
    });
    
    $header.append($title, $time);
    $textareaWrapper.append($textarea, $invalidTooltip);
    $buttonWrapper.append($smallText.append($saveButton, $cancelButton));
    
    commentSection.empty().append($header, $textareaWrapper, $buttonWrapper);
}
  
function createCommentInputBlock(doctor) {
    const commentsContent = $('#comments-container');
    
    const $commentInputBlock = $('<div>', { class: 'card mb-3 add-comment-card', id: 'add-comment' });
    const $cardBody = $('<div>', { class: 'card-body' });
    
    const $dFlex = $('<div>', { class: 'd-flex flex-start' });
    const $avatar = $('<img>', { 
        class: 'rounded-circle shadow-1-strong me-3', 
        src: '/static/images/default-avatar.png', 
        alt: 'avatar', 
        width: 64, 
        height: 64 
    });
    const $flexGrow = $('<div>', { class: 'flex-grow-1 flex-shrink-1' });
    
    const $header = $('<div>', { class: 'd-flex justify-content-between align-items-center mb-3' });
    const $doctorName = $('<h6>', { class: 'text-primary fw-bold', text: doctor });
    
    const $commentTextareaContainer = $('<div>', { class: 'mb-3 position-relative' });
    const $commentTextarea = $('<textarea>', { placeholder: 'Введите ваш комментарий здесь', rows: 4, class: 'form-control', id: 'comment-textarea' });
    const $invalidTooltip = $('<div>', { class: 'invalid-tooltip', text: 'Комментарий не должен быть пустым' });
    
    const $buttonContainer = $('<div>', { class: 'mt-1 text-end' });
    const $saveButton = $('<button>', { class: 'btn btn-theme', text: 'Сохранить', click: addComment });
    
    $header.append($doctorName);
    $commentTextareaContainer.append($commentTextarea, $invalidTooltip);
    $buttonContainer.append($saveButton);
    
    $flexGrow.append($header, $commentTextareaContainer, $buttonContainer);
    $dFlex.append($avatar, $flexGrow);
    $cardBody.append($dFlex);
    $commentInputBlock.append($cardBody);
    
    commentsContent.prepend($commentInputBlock);
}
  
function addComment() {
    const commentInput = $('#comment-textarea');
    const addedComment = commentInput.val();
    
    if (addedComment.trim() === '') {
        commentInput.addClass('is-invalid');
        return;
    } else {
        commentInput.removeClass('is-invalid');
    }
    
    webSocket.send(JSON.stringify({
        action: 'add_comment',
        request_id: requestId,
        comment: addedComment,
        room_id: requestId
    }));
}

function addCommentElement(comment) {
    const commentsContent = $('#comments-container');
    const $commentBlock = generateCommentElement(comment);
    let addCommentBlock = $('#add-comment');

    if (comment.editable) {
        addCommentBlock.remove();
        addCommentBlock = $('#add-comment');
    }
    
    const editableComment = $(`#comment-${comment.id}`);
    if (editableComment.length && comment.editable) {
        editableComment.replaceWith($commentBlock);
    } else if (addCommentBlock.length && !editableComment.length) {
        $commentBlock.insertAfter(addCommentBlock);
    } else {
        commentsContent.prepend($commentBlock);
    }
}

function saveComment(id) {
    const commentInput = $('#comment-textarea');
    const updatedComment = commentInput.val();
  
    if (updatedComment.trim() === '') {
        commentInput.addClass('is-invalid');
        return;
    } else {
        commentInput.removeClass('is-invalid');
    }

    webSocket.send(JSON.stringify({
        action: 'edit_comment',
        room_id: requestId,
        request_id: requestId,
        comment_id: id,
        comment: updatedComment
    }));
}

function editCommentElement(comment) {
    var editableComment = $(`#comment-${comment.old_id}`);
    const $commentBlock = generateCommentElement(comment);
    let addCommentBlock = $('#add-comment');

    if (comment.editable) {
        addCommentBlock.remove();
        addCommentBlock = $('#add-comment');
    
        if (editableComment.length) {
            editableComment.replaceWith($commentBlock);
            return;
        }
    }
    
    if (editableComment.length) {
        editableComment.replaceWith($commentBlock);
    } else if (addCommentBlock.length) {
        $commentBlock.insertAfter(addCommentBlock);
    } else {
        const commentsContent = $('#comments-container');
        commentsContent.prepend($commentBlock);
    }
}

function deleteComment(id) {
    webSocket.send(JSON.stringify({
        action: 'delete_comment',
        room_id: requestId,
        request_id: requestId,
        comment_id: id
    }));
}
  
function cancelEditComment(id, doctor, comment, time) {
    const commentBlock = $(`#comment-${id}`);
    const commentSection = commentBlock.find(".editable-comment-content");

    const $commentBlock = createCommentBlock(id, doctor, comment, time, true);
    commentSection.empty()
    commentSection.append($commentBlock.container1);
    if ($commentBlock.container2) {
        commentSection.append($commentBlock.container2);
    }
}
