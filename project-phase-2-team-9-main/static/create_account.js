const form = document.getElementById('form')   

form.addEventListener('submit', (e) => {
    //create_account
    const email = document.querySelector('#email').value
    const pass = document.querySelector('#password').value
    const fname = document.querySelector('#firstname').value
    const lname = document.querySelector('#lastname').value
    const address = document.querySelector('#address').value
    const ssn = document.querySelector('#ssn').value

    let messages = []
    if (!/^.+@.+$/.test(email) || email.length > 50) {
        messages.push('Invalid email')
    }
    if (pass.length > 50) {
        messages.push('Password is too long')
    }
    if (fname.length > 50) {
        messages.push('Name cannot be longer than 50 characters')
    }
    if (!/^[a-zA-Z]+$/.test(fname)) {
        messages.push('First name must be letters only')
    }
    if (lname.length > 50) {
        messages.push('Last name cannot be longer than 50 characters')
    }
    if (!/^[a-zA-Z]+$/.test(lname)) {
        messages.push('Last name must be letters only')
    }
    if (address.length > 100) {
        messages.push('Address cannot be longer than 100 characters')
    }
    if (ssn.length > 9 || ssn.length < 9 || !/^\d+$/.test(ssn)) {
        messages.push('SSN is invalid. Must be 9 numbers')
    }

    if (messages.length > 0 ) {
        e.preventDefault()
        messages = messages.join(', ')
        alert(messages)
    }
})