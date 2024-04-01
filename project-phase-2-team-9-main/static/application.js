const form = document.getElementById('fapp')   
form.addEventListener('submit', (e) => {
    //semester
    const semester = document.querySelector('#semester').value
    const year = parseInt(document.querySelector('#year').value)
    const currentDate = new Date();
    const currentYear = currentDate.getFullYear()
    const currentMonth = currentDate.getMonth()

    //Degree and GRE
    const degree = document.querySelector('#degree').value
    let total = document.querySelector('#total').value
    let verbal = document.querySelector('#verbal').value
    let quant = document.querySelector('#quant').value
    let yearexam = document.querySelector('#yearexam').value 
    let score = document.querySelector('#score').value
    const subject = document.querySelector('#subject').value
    let toefl = document.querySelector('#toefl').value
    let dateexam = document.querySelector('#dateexam').value

    //Past Degree BS/BA
    const bsba = document.querySelector('#bsba')
    let gpa2 = document.querySelector('#gpa2').value
    const major2 = document.querySelector('#major2').value
    let pdyear2 = document.querySelector('#pdyear2').value
    const university2 = document.querySelector('#university2').value

    //Past Degree MS
    const ms = document.querySelector('#ms')
    let gpa = document.querySelector('#gpa').value
    const major = document.querySelector('#major').value
    let pdyear = document.querySelector('#pdyear').value
    const university = document.querySelector('#university').value

    //Rec Letter
    const writer = document.querySelector('#writer').value
    const email = document.querySelector('#email').value
    const title = document.querySelector('#title').value
    const affiliation = document.querySelector('#affiliation').value

    let messages = []
        
    //Semester
    //if past Jan
    if (currentMonth >= 0 && currentMonth < 8) {
        if (semester === 'fall' && year === (currentYear+1)) {
            messages.push('You cannot apply more than 2 semesters in the future')
        }
        if (semester === 'spring' && year === currentYear) {
            messages.push('You cannot apply to this semester anymore')
        }
    }
    //if past august
    if (currentMonth >= 8) {
        if (semester === 'spring' && year === currentYear) {
            messages.push('You cannot apply for a past semester')
        }
        if (semester === 'fall' && year === currentYear) {
            messages.push('You cannot apply to this semester anymore')
        }
    }
    if (degree === 'PhD') {
        if (total === '') {
            messages.push('You must fill in the GRE Total field')
        }
        else if (!/^\d+$/.test(total) || total.length !== 3) {
            messages.push('Total score must be between 260 and 340')
        }
        else if (/^\d+$/.test(total)) {
            if (parseInt(total) > 340 || parseInt(total) < 260) {
                messages.push('Total score must be between 260 and 340')
            }
            if (/^\d+$/.test(verbal) && /^\d+$/.test(quant)) {
                if (parseInt(total) !== (parseInt(quant) + parseInt(verbal))) {
                    messages.push('Total should be Verbal + Quantitative score')
                }
            }
        }
        if (verbal === '') {
            messages.push('You must fill in the GRE Verbal field')
        }
        else if (!/^\d+$/.test(verbal) || verbal.length !== 3) {
            messages.push('Verbal score must between 130 and 170')
        }
        else if (/^\d+$/.test(verbal)) {
            if (parseInt(verbal) > 170 || parseInt(verbal) < 130) {
                messages.push('Verbal score must be between 130 and 170')
            }
        }
        if (quant === '') {
            messages.push('You must fill in the GRE Quantitative field')
        }
        else if (!/^\d+$/.test(quant) || quant.length !== 3) {
            messages.push('Quantitative score must between 130 and 170')
        }
        else if (/^\d+$/.test(quant)) {
            if (parseInt(quant) > 170 || parseInt(quant) < 130) {
                messages.push('Quantitative score must be between 130 and 170')
            }
        }
        if (yearexam === '') {
            messages.push('You must fill in the GRE Year of Exam field')
        }
        else if (!/^\d+$/.test(yearexam) || yearexam.length !== 4) {
            messages.push('Year of the exam must be a valid year')
        }
        else if (/^\d+$/.test(yearexam)) {
            if (parseInt(yearexam) > currentYear) {
                messages.push('Year of the exam cannot be in the future')
            }
        }
        if (score !== '') {
            if (subject === '') {
                messages.push('Please fill in the GRE Advanced Subject field')
            }
            if (!/^\d+$/.test(score) || score.length !== 3) {
                messages.push('Score must be a number between 200 and 990')
            }
            else if (/^\d+$/.test(score)) {
                if (parseInt(score) > 990 || parseInt(score) < 200){
                    messages.push('Score must be a number between 200 and 990')
                }
            }
        }
        if (subject !== '') {
            if (score === '') {
                messages.push('Please fill in the GRE Advanced Score field')
            }
            if (subject.length > 30) {
                messages.push('Subject must be under 30 characters')
            }
            if(!/^[a-zA-Z\s]+$/.test(subject)) {
                messages.push('Subject must only include letters')
            }
        }

        if (toefl !== '') {
            if (dateexam === '') {
                messages.push('Please fill in the Date of Exam field')
            }
            if (!/^\d+$/.test(toefl) || toefl.length > 3 || toefl.length < 1) {
                messages.push('TOEFL must be a number between 0 and 120')
            }
            else if (/^\d+$/.test(toefl)) {
                if (parseInt(toefl) > 120 || parseInt(toefl) < 0) {
                    messages.push('TOEFL must be a number between 0 and 120')
                }
            }
        }
        if (dateexam !== '') {
            if (toefl === '') {
                messages.push('Please fill in the TOEFL field')
            }
            if (!/^\d+$/.test(dateexam) || dateexam.length !== 4) {
                messages.push('Exam date must be a valid year')
            }
            else if (/^\d+$/.test(dateexam)) {
                if (parseInt(dateexam) > currentYear) {
                    messages.push('Exam date cannot be in the future')
                }
            }
        }
        //Past degree MS
        if (!ms.checked) {
            messages.push('You have to check the MS box')
        }
        if (gpa === '' || major === '' || pdyear === '' || university === '') {
            messages.push('Must fill out Masters information')
        }
        if (!/^[0-4]\.\d{2}$/.test(gpa) || gpa.length !== 4) {
            messages.push('MS GPA must be a decimal number between 0.00 and 4.00')
        }
        if (major.length > 50) {
            messages.push('MS major must be under 50 characters')
        }
        if(!/^[a-zA-Z\s]+$/.test(major)) {
            messages.push('MS major must only include letters')
        }
        if (!/^\d+$/.test(pdyear) || pdyear.length !== 4) {
            messages.push('MS graduation year must be a valid year')
        }
        else if (/^\d+$/.test(pdyear)) {
            if (parseInt(pdyear) > currentYear) {
                messages.push('BS/BA graduation date cannot be in the future')
            }
            if ((/^\d+$/.test(pdyear2) && pdyear2.length === 4) && (parseInt(pdyear) < parseInt(pdyear2))) {
                messages.push('MS graduation date cannot be before BS/BA gradutation date')
            }
        }   
        if (university.length > 50) {
            messages.push('MS university must be under 50 characters')
        }  
        if(!/^[a-zA-Z\s]+$/.test(university)) {
            messages.push('MS university must only include letters')
        }         
    }

    if (degree !== 'PhD') {
        if ((total !== '' || verbal !== '' || quant !== '' || yearexam !== '') || (total !== '' && verbal !== '' && quant !== '' && yearexam !== '')) {
            if ((!/^\d+$/.test(total) || total.length !== 3)) {
                messages.push('Total score must be between 260 and 340')
            }
            else if (/^\d+$/.test(total)) {
                if (parseInt(total) > 340 || parseInt(total) < 260) {
                    messages.push('Total score must be between 260 and 340')
                }
                if (/^\d+$/.test(verbal) && /^\d+$/.test(quant)) {
                    if (parseInt(total) !== (parseInt(quant) + parseInt(verbal))) {
                        messages.push('Total should be Verbal + Quantitative score')
                    }
                }
            }
            if ((!/^\d+$/.test(verbal) || verbal.length !== 3)) {
                messages.push('Verbal score must between 130 and 170')
            }
            else if (/^\d+$/.test(verbal)) {
                if (parseInt(verbal) > 170 || parseInt(verbal) < 130) {
                    messages.push('Verbal score must be between 130 and 170')
                }
            }
            if ((!/^\d+$/.test(quant) || quant.length !== 3)) {
                messages.push('Quantitative score must between 130 and 170')
            }
            else if (/^\d+$/.test(quant)) {
                if (parseInt(quant) > 170 || parseInt(quant) < 130) {
                    messages.push('Quantitative score must be between 130 and 170')
                }
            }
            if ((!/^\d+$/.test(yearexam) || yearexam.length !== 4)) {
                messages.push('Year of the exam must be a valid year')
            }
            else if (/^\d+$/.test(yearexam)) {
                if (parseInt(yearexam) > currentYear) {
                    messages.push('Year of the exam cannot be in the future')
                }
            }
        }
        if ((score !== '' || subject !== '') || (score !== '' && subject !== '')) {
            if ((!/^\d+$/.test(score) || score.length !== 3)) {
                messages.push('Score must be a number between 200 and 990')
            }
            else if (/^\d+$/.test(score)) {
                if (parseInt(score) > 990 || parseInt(score) < 200){
                     messages.push('Score must be a number between 200 and 990')
                }
            }
            if (subject.length > 30) {
                messages.push('Subject must be under 30 characters')
            }
            if(!/^[a-zA-Z\s]+$/.test(subject)) {
                messages.push('Subject must only include letters')
            }
        }
        if ((dateexam !== '' || toefl !== '') || (dateexam !== '' && toefl !== '')){
            if ((!/^\d+$/.test(toefl) || toefl.length > 3 || toefl.length < 1)) {
                messages.push('TOEFL must be a number between 0 and 120')
            }
            else if (/^\d+$/.test(toefl)) {
                if (parseInt(toefl) > 120 || parseInt(toefl) < 0) {
                    messages.push('TOEFL must be a number between 0 and 120')
                }
            }
            if ((!/^\d+$/.test(dateexam) || dateexam.length !== 4)) {
                messages.push('Exam date must be a valid year')
            }
            else if (/^\d+$/.test(dateexam)) {
                if (parseInt(dateexam) > currentYear) {
                    messages.push('Exam date cannot be in the future')
                }
            }
        }             
    }
    
    //Past degree BS/BA   
    if ((ms.checked || pdyear.length > 0 || gpa.length > 0 || major.length > 0 || university.length > 0) && (degree !== 'PhD')) {
        messages.push("Either choose the PhD degree or delete the Master's fields")
    }   
    if (!bsba.checked) {
        messages.push('You have to check the BS/BA box')
    }
    if (!/^[0-4]\.\d{2}$/.test(gpa2) || gpa2.length !== 4) {
        messages.push('BS/BA GPA must be a decimal number between 0.00 and 4.00')
    }
    if (major2.length > 50) {
        messages.push('BS/BA major must be under 50 characters')
    }
    if(!/^[a-zA-Z\s]+$/.test(major2)) {
        messages.push('BS/BA major must only include letters')
    }
    if (!/^\d+$/.test(pdyear2) || pdyear2.length !== 4) {
        messages.push('BS/BA graduation year must be a valid year')
    }
    else if (/^\d+$/.test(pdyear2)) {
        if (parseInt(pdyear2) > currentYear) {
            messages.push('BS/BA graduation date cannot be in the future')
        }
    }   
    if (university2.length > 50) {
        messages.push('BS/BA university must be under 50 characters')
    }     
    if(!/^[a-zA-Z\s]+$/.test(university2)) {
        messages.push('BS/BA university must only include letters')
    }     

    //Rec letter
    if (!/^[a-zA-Z\s]+$/.test(writer)) {
        messages.push('Letter writer must only include letters')
    }
    if (writer.length > 30) {
        messages.push('Name is too long (Max 30 characters)')
    }
    if (!/^.+@.+$/.test(email) || email.length > 50) {
        messages.push('Invalid recommender email')
    }
    if (title.length > 30) {
        messages.push('Title is too long')
    }
    if (!/^[a-zA-Z\s]+$/.test(title)) {
        messages.push('Title must only include letters')
    }
    if (affiliation.length > 30) {
        messages.push('Affiliation is too long')
    }
    if (!/^[a-zA-Z\s]+$/.test(affiliation)) {
        messages.push('Affiliation must only include letters')
    }
    // rec2
    if (!/^[a-zA-Z\s]+$/.test(writer2)) {
        messages.push('Letter writer must only include letters')
    }
    if (writer2.length > 30) {
        messages.push('Name is too long (Max 30 characters)')
    }
    if (!/^.+@.+$/.test(email2) || email2.length > 50) {
        messages.push('Invalid recommender email')
    }
    if (title2.length > 30) {
        messages.push('Title is too long')
    }
    if (!/^[a-zA-Z\s]+$/.test(title2)) {
        messages.push('Title must only include letters')
    }
    if (affiliation2.length > 30) {
        messages.push('Affiliation is too long')
    }
    if (!/^[a-zA-Z\s]+$/.test(affiliation2)) {
        messages.push('Affiliation must only include letters')
    }
    // rec3
    if (!/^[a-zA-Z\s]+$/.test(writer3)) {
        messages.push('Letter writer must only include letters')
    }
    if (writer3.length > 30) {
        messages.push('Name is too long (Max 30 characters)')
    }
    if (!/^.+@.+$/.test(email3) || email3.length > 50) {
        messages.push('Invalid recommender email')
    }
    if (title3.length > 30) {
        messages.push('Title is too long')
    }
    if (!/^[a-zA-Z\s]+$/.test(title3)) {
        messages.push('Title must only include letters')
    }
    if (affiliation3.length > 30) {
        messages.push('Affiliation is too long')
    }
    if (!/^[a-zA-Z\s]+$/.test(affiliation3)) {
        messages.push('Affiliation must only include letters')
    }

    if (messages.length > 0 ) {
        e.preventDefault()
        messages = messages.join('\n')
        alert(messages)
    }      
})