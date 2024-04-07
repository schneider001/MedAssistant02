import LazyLoadTable from './LazyLoadTable.js';
import { openRequestInfoModal } from './requestInfoModal.js';
import { showError } from "./main.js";

$(document).ready(function() {
    const patientsTable = new LazyLoadTable('patients-table', '/load_patients');
    let requestHistoryTable;

    $('#patients-table').on('click', 'tbody tr', function() {
        const patientId = $(this).find('td:first').text();
        
        if (isNaN(patientId)) {
            return;
        }
    
        const loadSection = document.getElementById('patient-load-section');
        const dataSection = document.getElementById('patient-data-section');
    
        loadSection.style.display = 'block';
        dataSection.style.display = 'none';
    
        $.ajax({
            url: '/get_patient_info',
            method: 'GET',
            data: { patient_id: patientId },
            success: function(data) {
                loadSection.style.display = 'none';
                dataSection.style.display = 'block';
                $('#name').text(data.name);
                const dateObject = new Date(data.birthDate * 1000);
                const formattedTime = `${dateObject.getFullYear()}-${(dateObject.getMonth() + 1).toString().padStart(2, '0')}-${dateObject.getDate().toString().padStart(2, '0')}`;
                $('#birth-date').text(formattedTime);
                $('#age').text(data.age);
                $('#oms').text(data.oms);
                $('#sex').text(function() {
                    if (data.sex === 'MALE') {
                        return 'мужской';
                    } else if (data.sex === 'FEMALE') {
                        return 'женский';
                    } else {
                        return 'другой';
                    }
                });

                if (data.photo_url) {
                    $('.patient-photo').attr('src', data.photo_url);
                }

                if (requestHistoryTable) {
                    requestHistoryTable.removeEventListeners();
                    $('#request-history-table').off('click', 'tbody tr');
                }
                requestHistoryTable = new LazyLoadTable('request-history-table', '/load_patient_history', patientId);

                $('#request-history-table').on('click', 'tbody tr', function() {
                    var requestId = $(this).find('td:first').text();
                
                    if (isNaN(requestId)) {
                        return;
                    }
            
                    openRequestInfoModal('by_id', { request_id: requestId });
                });
            },
            error: function(xhr, status, error) {
                console.error('Ошибка при получении информации о пациенте: ' + error);
                var errorMessage = "Произошла ошибка при получении информации о пациенте на сервере. Пожалуйста, попробуйте еще раз.";
                showError(errorMessage);
            }
        });
    
        $('#patientModal').modal('show');
    });
})