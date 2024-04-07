import { openRequestInfoModal } from "./requestInfoModal.js";
import "./select2adapters.js";
import { showError } from "./main.js";

$(document).ready(function() {
    $('#symptoms').select2({
        theme: 'bootstrap-5',
        closeOnSelect: false,
	    allowClear: true,
        minimumInputLength: 4,
        ajax: {
            url: '/load_symptoms',
            dataType: 'json',
            delay: 250,
            data: function(params) {
                return {
                    search: params.term,
                    page: params.page || 1
                };
            },
            processResults: function(data, params) {
                params.page = params.page || 1;
                
                data.results.forEach(function(result) {
                    result.symptom_id = result.id;
                });

                return {
                    results: data.results,
                    pagination: {
                        more: data.pagination.more
                    }
                };
            },
            params: {
                error: function(response) {
                    var errorMessage = "Произошла ошибка при загрузке симптомов на сервере. Пожалуйста, попробуйте еще раз.";
                    showError(errorMessage);
                }
            },
            cache: true
        },
        language: {
            errorLoading: () => 'Невозможно загрузить симптомы',
            inputTooLong: () => 'Слишком много символов',
            inputTooShort: () => 'Введите минимум 4 символа',
            maximumSelected: () => 'Выбрано максимальное количество симптомов',
            noResults: () => $('<div>', { class: 'text-center' }).text('Нет результатов'),
            removeAllItems: () => 'Удалить все симптомы',
            removeItem: () => 'Удалить симптом',
            search: () => 'Поиск',
            searching: () => $('<div>', { class: 'text-center' }).append($('<div>', { class: 'spinner-border spinner-border-sm', role: 'status' })
                    .append($('<span>', { class: 'visually-hidden' }).text('Загрузка...'))),
            loadingMore: () => $('<div>', { class: 'text-center' }).append($('<div>', { class: 'spinner-border spinner-border-sm', role: 'status' })
                    .append($('<span>', { class: 'visually-hidden' }).text('Загрузка...')))
        },  
        templateResult: function(option) {
            if (!option.symptom_id) { return option.text; }
            return option.name;
        },
        templateSelection: function(option) {
            if (!option.id) { return option.text; }
            return option.name;
        }
    });

    $('#patientname').select2({
        theme: 'bootstrap-5',
        placeholderForSearch: 'Поиск...',
        dropdownAdapter: $.fn.select2.amd.require("PatientsDropdownAdapter"),
        closeOnSelect: true,
        minimumInputLength: 4,
        ajax: {
            url: '/load_patients',
            dataType: 'json',
            delay: 250,
            data: function(params) {
                return {
                    search: params.term,
                    page: params.page || 1
                };
            },
            processResults: function(data, params) {
                params.page = params.page || 1;

                return {
                    results: data.results,
                    pagination: {
                        more: data.pagination.more
                    }
                };
            },
            params: {
                error: function(response) {
                    var errorMessage = "Произошла ошибка при загрузке пациентов на сервере. Пожалуйста, попробуйте еще раз.";
                    showError(errorMessage);
                }
            },
            cache: true
        },
        language: {
            errorLoading: () => 'Невозможно загрузить результаты',
            inputTooLong: () => 'Слишком много символов',
            inputTooShort: () => 'Введите минимум 4 символа',
            maximumSelected: () => 'Выбрано максимальное количество элементов',
            noResults: () => $('<div>', { class: 'text-center' }).text('Нет результатов'),
            removeAllItems: () => 'Удалить все элементы',
            removeItem: () => 'Удалить элемент',
            search: () => 'Поиск',
            searching: () => $('<div>', { class: 'text-center' }).append($('<div>', { class: 'spinner-border spinner-border-sm', role: 'status' })
                    .append($('<span>', { class: 'visually-hidden' }).text('Загрузка...'))),
            loadingMore: () => $('<div>', { class: 'text-center' }).append($('<div>', { class: 'spinner-border spinner-border-sm', role: 'status' })
                    .append($('<span>', { class: 'visually-hidden' }).text('Загрузка...')))
        },   
        templateResult: function(option) {
            if (!option.id) { return option.text; }
            
            var $row = $('<div>', { class: 'row' });
            var $nameCol = $('<div>', { class: 'col', text: option.name });
            var $omsCol = $('<div>', { class: 'col-3', text: option.oms });

            $row.append($nameCol, $omsCol);
            return $row;
        },
        templateSelection: function(option) {
            if (!option.id) { return option.text; }

            const container = $('<div>').css('display', 'flex').css('justify-content', 'space-between');
            container.attr('title', `Имя: ${option.name}, Полис ОМС: ${option.oms}`);
        
            const nameWrapper = $('<div>');
            nameWrapper.append($('<span>').text('Имя: ').css('color', '#888'));
            nameWrapper.append($('<span>').text(option.name));
        
            const omsWrapper = $('<div>');
            omsWrapper.append($('<span>').text('Полис ОМС: ').css('color', '#888'));
            omsWrapper.append($('<span>').text(option.oms));
            nameWrapper.css('margin-right', '15px');
            
            return container.append(nameWrapper, omsWrapper);
        }
    })

    $('#requestForm').submit(function(e) {
        e.preventDefault();
        var selectedData = $('#patientname').select2('data');
        var selectedOption = selectedData[0];
        var symptoms = $('#symptoms').select2('data').map(function(item) {
            return item.id;
        });
        
        openRequestInfoModal('new', { id: selectedOption.id, name: selectedOption.name, oms: selectedOption.oms, symptoms: symptoms });
    });
})