document.addEventListener('DOMContentLoaded', () => {
    // event listener approving leaves (manager side)
    document.querySelectorAll('.leave_buttons').forEach(button => {
        button.addEventListener('click', () => manager_approve_leave(button))
    });

    // for adding new employees
    if (document.getElementById('add_employee_form')) {
        document.getElementById('add_employee_form').onsubmit = add_employee
    }
    
    // show how many days leave when hover over
    if (document.getElementById('how_many_days_button')) {
        document.getElementById('how_many_days_button').addEventListener('click', how_many_days_leave)
    }
})

// when user clicks on approve or reject button for a particular leave
function manager_approve_leave(button) {
    let action, leave_id;
    [action, leave_id] = button.id.split(' ')
    console.log(action, leave_id)

    fetch('approve_reject_leave', {
        method: 'PUT',
        body: JSON.stringify({
            action: action,
            leave_id: leave_id
        })
    })
    .then(response => response.json())
    .then(response => {
        console.log(response)

        if (action === 'approve') {
            // show in approved leaves
            fetch_approved_leaves()
        }
        // remove table row
        const leave_tr = document.getElementById(`tr_${leave_id}`)
        console.log(leave_tr)
        leave_tr.remove()
    })
}

function fetch_approved_leaves() {
    fetch('approved_leaves_list')
    .then(response => response.json())
    .then(response => {
        console.log(response)

        // clear tbody contents
        const approved_tbody = document.querySelector('#approved_table tbody')
        approved_tbody.innerHTML = ''

        response.forEach(leave => {
            // create new table rows based on response 
            const new_tr = document.createElement('tr')
            new_tr.innerHTML = `<th scope="row">${leave.employee}</th><td>${leave.start}</td><td>${leave.end}</td><td>${leave.duration} days</td>`
            approved_tbody.append(new_tr)
        })
    })
}

function add_employee() {
    const input = document.getElementById('all_employee')
    console.log(input.value)

    fetch('add_employee', {
        method: 'PUT',
        body: JSON.stringify({
            employee:input.value
        })
    })
    .then(response => response.json())
    .then(response => {
        console.log(response)

        document.getElementById('add_employee_success_message').style.display = (response.success)? 'block' : 'none'
        document.getElementById('add_employee_failure_message').style.display = (response.success)? 'none' : 'block'
    })

    // prevents form from submitting
    return false
}

function how_many_days_leave() {
    const button = document.getElementById('how_many_days_button')
    const show_days_leave_p = document.getElementById('show_days_leave')
    const default_message = '__ day(s)'

    const startDate = document.getElementById('startDate').value
    const startAM = document.getElementById('startAM').checked
    const endDate = document.getElementById('endDate').value
    const endAM = document.getElementById('endAM').checked

    console.log(startDate, startAM, endDate, endAM)
    
    if (startDate.length > 0 && endDate.length > 0) {
        const start = new Date(startDate + 'T' + ((startAM)? '00:00:00' : '12:00:00'))
        const end = new Date(endDate + 'T' + ((endAM)? '00:00:00' : '12:00:00'))
        const duration = ((end - start) / (1000 * 60 * 60) + 12) / 24
        console.log(duration)
        show_days_leave_p.innerText = duration + ' day(s)'
    }
    else {
        console.log(default_message)
        show_days_leave_p.innerText = default_message
    }
}