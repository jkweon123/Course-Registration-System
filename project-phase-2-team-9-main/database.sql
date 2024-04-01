
-- Active: 1681753866142@@phase2-9.cb4scbzafh0g.us-east-1.rds.amazonaws.com@3306@university


DROP DATABASE IF EXISTS university;
CREATE DATABASE university

    DEFAULT CHARACTER SET = 'utf8mb4';
use university;

SET FOREIGN_KEY_CHECKS=0;

DROP TABLE IF EXISTS users;
CREATE TABLE users (
    uid         int(8) AUTO_INCREMENT NOT NULL UNIQUE,
    fname       varchar(50) NOT NULL,
    lname       varchar(50) NOT NULL,
    email       varchar(50) NOT NULL UNIQUE,
    password    varchar(50) NOT NULL,
    address     varchar(100) NOT NULL,
    ssn         char(9) NOT NULL UNIQUE,
    PRIMARY KEY (uid)
);

DROP TABLE IF EXISTS user_types;
CREATE TABLE user_types (
    user_type   ENUM('Admin', 'Applicant', 'GS', 'CAC', 'Reviewer', 'Advisor', 'Student', 'Alumni', 'Instructor') NOT NULL,
    uid         int(8)      NOT NULL,
    PRIMARY KEY (user_type, uid),
    FOREIGN KEY (uid) REFERENCES users(uid)
);

DROP TABLE IF EXISTS applications;
CREATE TABLE applications (
    appid       int(5) AUTO_INCREMENT NOT NULL UNIQUE,
    uid         int(8) NOT NULL UNIQUE,
    status      enum('incomplete', 'complete', 'admitted', 'denied') NOT NULL,
    transcript  enum('T', 'F') NOT NULL,
    degree      enum('MS', 'PhD') NOT NULL,
    past_d1     int(5) NOT NULL,
    past_d2     int(5),
    semester    enum('Fall', 'Spring') NOT NULL,
    year        int(4) NOT NULL,
    experience  varchar(300) NOT NULL,
    aoi         varchar(300) NOT NULL,
    letter      int(5) DEFAULT NULL,
    letter2     int(5) DEFAULT NULL,
    letter3     int(5) DEFAULT NULL,
    review      int(5) DEFAULT NULL,
    gre         int(5) DEFAULT NULL,
    PRIMARY KEY (appid),
    FOREIGN KEY (past_d1) REFERENCES degrees(degid),
    FOREIGN KEY (past_d2) REFERENCES degrees(degid),
    FOREIGN KEY (letter) REFERENCES recs(recid),
    FOREIGN KEY (letter2) REFERENCES recs(recid),
    FOREIGN KEY (letter3) REFERENCES recs(recid),
    FOREIGN KEY (review) REFERENCES reviews(revid),
    FOREIGN KEY (gre) REFERENCES gres(greid),
    FOREIGN KEY (uid) REFERENCES users(uid)
);

DROP TABLE IF EXISTS degrees;
CREATE TABLE degrees (
    degid       int(5) AUTO_INCREMENT NOT NULL UNIQUE,
    uid         int(8) NOT NULL,
    type        enum('BS/BA', 'MS') NOT NULL,
    gpa         decimal(3,2) NOT NULL, 
    major       varchar(50) NOT NULL,
    college     varchar(50) NOT NULL,
    year        int(4) NOT NULL,
    PRIMARY KEY (degid),
    Foreign Key (uid) REFERENCES users(uid)
);

DROP TABLE IF EXISTS gres;
CREATE TABLE gres (
    greid       int(5) AUTO_INCREMENT NOT NULL UNIQUE,
    uid         int(8) NOT NULL UNIQUE,
    total       int(3) DEFAULT NULL,
    verbal      int(3) DEFAULT NULL,
    quant       int(3) DEFAULT NULL,
    year        int(4) DEFAULT NULL,
    toefl       int(3) DEFAULT NULL,
    score       int(3) DEFAULT NULL,
    subject     varchar(30) DEFAULT NULL,
    date        int(4) DEFAULT NULL,
    PRIMARY KEY (greid),
    FOREIGN KEY (uid) REFERENCES users(uid)
);

DROP TABLE IF EXISTS reviews;
CREATE TABLE reviews (
    revid       int(5) AUTO_INCREMENT NOT NULL UNIQUE,
    uid         int(8) NOT NULL,
    rating      ENUM('0','1','2','3') NOT NULL,
    rec_num     ENUM('1','2','3') NOT NULL,
    rating1      ENUM('1','2','3','4','5'),
    generic1     ENUM("y","n"),
    credible1    ENUM("y","n"),
    rating2      ENUM('1','2','3','4','5'),
    generic2     ENUM("y","n"),
    credible2    ENUM("y","n"),
    rating3      ENUM('1','2','3','4','5'),
    generic3     ENUM("y","n"),
    credible3    ENUM("y","n"),
    deficiency  varchar(100),
    reason      char(1) NOT NULL,
    advisor     varchar(30),
    comments    varchar(40),
    reviewer_id int(8) NOT NULL,
    PRIMARY KEY (revid),
    FOREIGN KEY (uid) REFERENCES users(uid),
    FOREIGN KEY (reviewer_id) REFERENCES users(uid)
);

DROP TABLE IF EXISTS recs;
CREATE TABLE recs (
    recid       int(5) AUTO_INCREMENT NOT NULL UNIQUE,
    uid         int(8) NOT NULL,
    writer      varchar(30) NOT NULL,
    email       varchar(50) NOT NULL UNIQUE,
    title       varchar(30) NOT NULL,
    affiliation varchar(30) NOT NULL,
    message     varchar(200) DEFAULT NULL,
    PRIMARY KEY (recid),
    FOREIGN KEY (uid) REFERENCES users(uid)
);

DROP TABLE IF EXISTS student;
CREATE TABLE student (
    uid         INT(8), 
    advisorid   INT, 
    GPA         DECIMAL(3,2), 
    program     ENUM("MS","PhD") NOT NULL, 
    rdygrad     boolean, 
    year        INT(4), 
    PRIMARY KEY (uid),
    FOREIGN KEY (uid) REFERENCES users(uid)
); 

DROP TABLE IF EXISTS faculty; 
CREATE TABLE faculty (
    uid         INT(8), 
    department  VARCHAR(50),
    PRIMARY KEY (uid),
    FOREIGN KEY (uid) REFERENCES users(uid)
); 
DROP TABLE IF EXISTS course_info; 
CREATE TABLE course_info (
    dname       VARCHAR(50), 
    cnum        int(4), 
    title       VARCHAR(50), 
    credits     INT(1), 
    PRIMARY KEY (dname, cnum) 
); 
DROP TABLE IF EXISTS form1; 
CREATE TABLE form1 (
    uid         INT(8), 
    courseDept  varchar(50), 
    courseNum   int(4), 
    hold        BOOLEAN,
    PRIMARY KEY (uid, courseDept, courseNum), 
    FOREIGN KEY (uid) REFERENCES student(uid) ON DELETE CASCADE, 
    FOREIGN KEY (courseDept, courseNum) REFERENCES course_info(dname, cnum)
); 

DROP TABLE IF EXISTS prerequisite; 
CREATE TABLE prerequisite (
    dname           VARCHAR(50), 
    cnum            int(4), 
    prereq_type     ENUM('1', '2'), 
    prereq_dname    VARCHAR(50), 
    prereq_cnum     int(4),
    PRIMARY KEY (dname, cnum, prereq_type), 
    FOREIGN KEY (dname, cnum) REFERENCES course_info(dname, cnum)
); 

DROP TABLE IF EXISTS course_to_class; 
CREATE TABLE course_to_class (
    cid         int(8),
    dname       varchar(50),
    cnum        int(4), 
    section     int(2),
    PRIMARY KEY (cid), 
    FOREIGN KEY (dname, cnum) REFERENCES course_info(dname, cnum)
); 
DROP TABLE IF EXISTS class_section; 
CREATE TABLE class_section (
    cid         int(8),
    csem        VARCHAR(50),
    cyear       VARCHAR(50),
    day         char,
    class_time  VARCHAR(20),
    fid         int(8),
    PRIMARY KEY (cid, csem, cyear), 
    FOREIGN KEY (cid) REFERENCES course_to_class (cid),
    FOREIGN KEY (fid) REFERENCES faculty(uid)
); 

DROP TABLE IF EXISTS transcript; 
CREATE TABLE transcript (
    stud_id     int(8),
    cid         int(8),
    csem        varchar(20),
    cyear       varchar(20),
    grade       varchar(4),
    PRIMARY KEY (stud_id, cid, csem, cyear),
    FOREIGN KEY (stud_id) REFERENCES users (uid),
    FOREIGN KEY (cid, csem, cyear) REFERENCES class_section (cid, csem, cyear)
); 

DROP TABLE IF EXISTS alumni; 
CREATE TABLE alumni (
    uid         INT(8),
    GPA         DECIMAL(3,2),
    grad_sem    VARCHAR(20),
    grad_year   INT(4),
    admit_year  INT(4),
    program     ENUM("MS","PhD") NOT NULL,
    PRIMARY KEY (uid), 
    FOREIGN KEY (uid) REFERENCES users(uid)
); 

DROP TABLE IF EXISTS thesis;
CREATE TABLE thesis(
  thesis LONGTEXT,
  uid INT(8),
  decision INT,
  PRIMARY KEY (uid), 
  FOREIGN KEY (uid) REFERENCES users(uid)
);

SET FOREIGN_KEY_CHECKS=1;

--User INFORMATION
INSERT INTO users VALUES (111111111,'admin', 'admminlname', 'admin@gmail.com', 'password', '123 abc st', '123456789');
INSERT INTO user_types VALUES('Admin', 111111111);

INSERT INTO users VALUES (22222222,'gs', 'gslname', 'gs@gmail.com', 'password', '123 abc st', '123456788');
INSERT INTO user_types VALUES('GS', 22222222);

INSERT INTO users VALUES (33333333,'cac', 'caclname', 'cac@gmail.com', 'password', '123 abc st', '123456780');
INSERT INTO user_types VALUES('CAC', 33333333);

INSERT INTO users VALUES (12345678,'narahari', 'naraharilname', 'narahari@gmail.com', 'password', '123 abc st', '123456799');
INSERT INTO faculty VALUES (12345678,'CSCI');
INSERT INTO user_types VALUES('Instructor', 12345678);
INSERT INTO user_types VALUES('Advisor', 12345678);
INSERT INTO user_types VALUES('Reviewer', 12345678);

INSERT INTO users VALUES (87654321, 'Choi', 'Choilname', 'choi@gmail.com', 'password', '123 abc st', '135678954'); 
INSERT INTO faculty VALUES (87654321, 'CSCI');
INSERT INTO user_types VALUES ('Instructor', 87654321); 

INSERT INTO users VALUES (55555555,'Paul','McCartney', 'pm@gmail.com', 'password', '123 abc st', '124145432'); 
INSERT INTO user_types VALUES ('Student', 55555555); 
INSERT INTO student VALUES (55555555, 12345678, null, "MS", false, 2023); 

INSERT INTO users VALUES (66666665,'George', 'Harrison', 'gh@gmail.com', 'password', '123 abc st', '123426709');
INSERT INTO user_types VALUES('Student', 66666665);
INSERT INTO student VALUES (66666665, 13131313, null, "MS", false, 2023); 

INSERT INTO users VALUES (12312312,'John', 'Lennon', 'john@gmail.com', 'password', '123 abc st', '111111111');
INSERT INTO user_types VALUES('Applicant', 12312312);

INSERT INTO users VALUES (666666666,'Ringo', 'Starr', 'ringo@gmail.com', 'password', '123 abc st', '222111111');
INSERT INTO user_types VALUES('Applicant', 666666666);

INSERT INTO users VALUES (00000003, 'Ringo', 'Starr2',  'ringo2@gmail.com', 'password', '123 abc st', '134245345');
INSERT INTO user_types VALUES('Student', 00000003); 
INSERT INTO student VALUES (00000003, 13131313, null, "PhD", false, 2023);

INSERT INTO users VALUES (12121212,'wood', 'woodlname', 'wood@gmail.com', 'password', '123 abc st', '123426799');
INSERT INTO user_types VALUES('Instructor', 12121212);
INSERT INTO user_types VALUES('Advisor', 12121212); 
INSERT INTO user_types VALUES('Reviewer', 12121212);
INSERT INTO faculty VALUES (12121212,'CSCI');

INSERT INTO users VALUES (13131313, 'Gabe', 'Parmer', 'gp@gmail.com', 'password', '123 abc st', '134569234');
INSERT INTO user_types VALUES ('Advisor', 13131313);
INSERT INTO faculty VALUES (13131313, 'CSCI'); 

INSERT INTO users VALUES (77777777, 'Eric', 'Clapton', 'ec@gmail.com', 'password', '123 abc st', '146436987'); 
INSERT INTO user_types VALUES ('Alumni', 77777777);
INSERT INTO alumni VALUES (77777777, 3.50, "Spring", 2014, 2010, "MS"); 
INSERT INTO thesis VALUES ('Hi my name is Eric Clapton and this is my thesis', 77777777, 0); 

INSERT INTO users VALUES(91827364, 'Alumni', 'Lname', 'alumni@gmail.com', 'password', '123 abc st', '91827364');
INSERT INTO user_types VALUES ('Alumni', 91827364);
INSERT INTO alumni VALUES(91827364, 3.50, "Fall", 2022, 2018, "MS");

INSERT INTO users VALUES(91825364, 'Alumni2', 'Lname', 'alumni2@gmail.com', 'password', '123 abc st', '91822364');
INSERT INTO user_types VALUES ('Alumni', 91825364);
INSERT INTO alumni VALUES(91825364, 3.50, "Fall", 2023, 2019, "MS");

INSERT INTO users VALUES (88888888, 'Billie', 'Holiday', 'billie@gmail.com', 'password', '123 abc st', '156789456');
INSERT INTO user_types VALUES ('Student', 88888888);
INSERT INTO student VALUES (88888888, null, null, "MS", false, 2023); 

INSERT INTO users VALUES (99999999, 'Diana', 'Krall', 'diana@gmail.com', 'password', '123 abc st', '156783456');
INSERT INTO user_types VALUES ('Student', 99999999);
INSERT INTO student VALUES (99999999, null, null, "MS", false, 2023); 

INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6221, 'SW Paradigms', 3);  
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6461, 'Computer Architecture', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6212, 'Algorithms', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6220, 'Machine Learning', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6232, 'Networks 1', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6233, 'Networks 2', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6241, 'Database 1', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6242, 'Database 2', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6246, 'Compilers', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6260, 'Multimedia', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6251, 'Cloud Computing', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6262, 'Graphics 1', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6283, 'Security 1', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6284, 'Cryptography', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6286, 'Network Security', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6339, 'Embedded Systems', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('CSCI', 6384, 'Cryptography 2', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('ECE', 6241, 'Communication Theory', 3); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('ECE', 6242, 'Information Theory', 2); 
INSERT INTO course_info (dname, cnum, title, credits) VALUES ('MATH', 6210, 'Logic', 2); 


INSERT INTO prerequisite (dname, cnum, prereq_type, prereq_dname, prereq_cnum) VALUES ('CSCI', 6233, '1', 'CSCI', 6232); 
INSERT INTO prerequisite (dname, cnum, prereq_type, prereq_dname, prereq_cnum) VALUES ('CSCI', 6242, '1', 'CSCI', 6241); 
INSERT INTO prerequisite (dname, cnum, prereq_type, prereq_dname, prereq_cnum) VALUES ('CSCI', 6246, '1', 'CSCI', 6461); 
INSERT INTO prerequisite (dname, cnum, prereq_type, prereq_dname, prereq_cnum) VALUES ('CSCI', 6246, '2', 'CSCI', 6212); 
INSERT INTO prerequisite (dname, cnum, prereq_type, prereq_dname, prereq_cnum) VALUES ('CSCI', 6251, '1', 'CSCI', 6461); 
INSERT INTO prerequisite (dname, cnum, prereq_type, prereq_dname, prereq_cnum) VALUES ('CSCI', 6283, '1', 'CSCI', 6212);
INSERT INTO prerequisite (dname, cnum, prereq_type, prereq_dname, prereq_cnum) VALUES ('CSCI', 6284, '1', 'CSCI', 6212);
INSERT INTO prerequisite (dname, cnum, prereq_type, prereq_dname, prereq_cnum) VALUES ('CSCI', 6286, '1', 'CSCI', 6283); 
INSERT INTO prerequisite (dname, cnum, prereq_type, prereq_dname, prereq_cnum) VALUES ('CSCI', 6286, '2', 'CSCI', 6232);
INSERT INTO prerequisite (dname, cnum, prereq_type, prereq_dname, prereq_cnum) VALUES ('CSCI', 6339, '1', 'CSCI', 6461);
INSERT INTO prerequisite (dname, cnum, prereq_type, prereq_dname, prereq_cnum) VALUES ('CSCI', 6339, '2', 'CSCI', 6212);
INSERT INTO prerequisite (dname, cnum, prereq_type, prereq_dname, prereq_cnum) VALUES ('CSCI', 6384, '1', 'CSCI', 6284);




INSERT INTO course_to_class VALUES (1, "CSCI", 6221, 1);
INSERT INTO course_to_class VALUES (2, "CSCI", 6461, 1);
INSERT INTO course_to_class VALUES (3, "CSCI", 6212, 1);
INSERT INTO course_to_class VALUES (4, "CSCI", 6232, 1);
INSERT INTO course_to_class VALUES (5, "CSCI", 6233, 1);
INSERT INTO course_to_class VALUES (6, "CSCI", 6241, 1);
INSERT INTO course_to_class VALUES (7, "CSCI", 6242, 1);
INSERT INTO course_to_class VALUES (8, "CSCI", 6246, 1);
INSERT INTO course_to_class VALUES (9, "CSCI", 6251, 1);
INSERT INTO course_to_class VALUES (11, "CSCI", 6260, 1);
INSERT INTO course_to_class VALUES (12, "CSCI", 6262, 1);
INSERT INTO course_to_class VALUES (13, "CSCI", 6283, 1);
INSERT INTO course_to_class VALUES (14, "CSCI", 6284, 1);
INSERT INTO course_to_class VALUES (15, "CSCI", 6286, 1);
INSERT INTO course_to_class VALUES (16, "CSCI", 6384, 1);
INSERT INTO course_to_class VALUES (17, "ECE", 6241, 1);
INSERT INTO course_to_class VALUES (18, "ECE", 6242, 1);
INSERT INTO course_to_class VALUES (19, "MATH", 6210, 1);
INSERT INTO course_to_class VALUES (20, "CSCI", 6339, 1);
INSERT INTO course_to_class VALUES (21, "CSCI", 6221, 2);
INSERT INTO course_to_class VALUES (22, "CSCI", 6461, 2);
INSERT INTO course_to_class VALUES (23, "CSCI", 6212, 2);
INSERT INTO course_to_class VALUES (24, "CSCI", 6232, 2);
INSERT INTO course_to_class VALUES (25, "CSCI", 6233, 2);
INSERT INTO course_to_class VALUES (26, "CSCI", 6241, 2);


INSERT INTO class_section VALUES (1, "Fall", "2023", "M", "15:00-17:30", 12345678);
INSERT INTO class_section VALUES (2, "Fall", "2023", "T", "15:00-17:30", 12345678);
INSERT INTO class_section VALUES (3, "Fall", "2023", "W", "15:00-17:30", 87654321); 
INSERT INTO class_section VALUES (4, "Fall", "2023", "M", "18:00-20:30", 12345678);
INSERT INTO class_section VALUES (5, "Fall", "2023", "T", "18:00-20:30", 12345678);
INSERT INTO class_section VALUES (6, "Fall", "2023", "W", "18:00-20:30", 12345678);
INSERT INTO class_section VALUES (7, "Fall", "2023", "R", "18:00-20:30", 12345678);
INSERT INTO class_section VALUES (8, "Fall", "2023", "T", "15:00-17:30", 12345678);
INSERT INTO class_section VALUES (9, "Fall", "2023", "M", "18:00-20:30", 12345678);
INSERT INTO class_section VALUES (11, "Fall", "2023", "R", "18:00-20:30", 12345678);
INSERT INTO class_section VALUES (12, "Fall", "2023", "W", "18:00-20:30", 12345678);
INSERT INTO class_section VALUES (13, "Fall", "2023", "T", "18:00-20:30", 12345678);
INSERT INTO class_section VALUES (14, "Fall", "2023", "M", "18:00-20:30", 12345678);
INSERT INTO class_section VALUES (15, "Fall", "2023", "W", "18:00-20:30", 12345678);
INSERT INTO class_section VALUES (16, "Fall", "2023", "W", "15:00-17:30", 12345678);
INSERT INTO class_section VALUES (17, "Fall", "2023", "M", "18:00-20:30", 12345678);
INSERT INTO class_section VALUES (18, "Fall", "2023", "T", "18:00-20:30", 12345678);
INSERT INTO class_section VALUES (19, "Spring", "2022", "W", "18:00-20:30", 12345678);
INSERT INTO class_section VALUES (20, "Spring", "2022", "R", "16:00-18:30", 12345678);
INSERT INTO class_section VALUES (21, "Spring", "2022", "R", "15:00-17:30", 12345678);
INSERT INTO class_section VALUES (22, "Spring", "2022", "W", "18:30-21:00", 12345678);
INSERT INTO class_section VALUES (23, "Fall", "2022", "W", "15:00-17:30", 12345678);
INSERT INTO class_section VALUES (24, "Fall", "2022", "T", "18:00-20:30", 12345678); 
INSERT INTO class_section VALUES (25, "Fall", "2023", "R", "16:00-18:30", 12345678);
INSERT INTO class_section VALUES (26, "Fall", "2023", "F", "15:00-17:30", 12345678);

INSERT INTO transcript (stud_id, cid, csem, cyear, grade)
VALUES
(55555555, 1, 'Fall', '2023', 'A'),
(55555555, 2, 'Fall', '2023', 'A'),
(55555555, 3, 'Fall', '2023', 'A'),
(55555555, 4, 'Fall', '2023', 'A'),
(55555555, 5, 'Fall', '2023', 'A'),
(55555555, 6, 'Fall', '2023', 'B'),
(55555555, 8, 'Fall', '2023', 'B'),
(55555555, 12, 'Fall', '2023', 'B'),
(55555555, 13, 'Fall', '2023', 'B'),
(55555555, 7, 'Fall', '2023', 'B');

--GH transcript--
INSERT INTO transcript (stud_id, cid, csem, cyear, grade)
VALUES
(66666665, 18, 'Fall', '2023', 'C'),
(66666665, 1, 'Fall', '2023', 'B'),
(66666665, 2, 'Fall', '2023', 'B'),
(66666665, 3, 'Fall', '2023', 'B'),
(66666665, 4, 'Fall', '2023', 'B'),
(66666665, 5, 'Fall', '2023', 'B'),
(66666665, 6, 'Fall', '2023', 'B'),
(66666665, 7, 'Fall', '2023', 'B'),
(66666665, 13, 'Fall', '2023', 'B'),
(66666665, 14, 'Fall', '2023', 'B');


INSERT INTO transcript (stud_id, cid, csem, cyear, grade)
VALUES
(66666665, 19, 'Spring', '2022', 'B'),
(66666665, 20, 'Spring', '2022', 'B'),
(66666665, 21, 'Spring', '2022', 'B'),
(66666665, 24, 'Fall', '2022', 'A'); 


--RS transcript-- 
INSERT INTO transcript (stud_id, cid, csem, cyear, grade)
VALUES
(00000003, 1, 'Fall', '2023', 'A'),
(00000003, 2, 'Fall', '2023', 'A'),
(00000003, 3, 'Fall', '2023', 'A'),
(00000003, 4, 'Fall', '2023', 'A'),
(00000003, 5, 'Fall', '2023', 'A'),
(00000003, 6, 'Fall', '2023', 'A'),
(00000003, 7, 'Fall', '2023', 'A'),
(00000003, 8, 'Fall', '2023', 'A'),
(00000003, 11, 'Fall', '2023', 'A'),
(00000003, 9, 'Fall', '2023', 'A'),
(00000003, 12, 'Fall', '2023', 'A');

--EC transcript--
INSERT INTO transcript (stud_id, cid, csem, cyear, grade)
VALUES
(77777777, 1, 'Fall', '2023', 'B'),
(77777777, 3, 'Fall', '2023', 'B'),
(77777777, 2, 'Fall', '2023', 'B'),
(77777777, 4, 'Fall', '2023', 'B'),
(77777777, 5, 'Fall', '2023', 'B'),
(77777777, 6, 'Fall', '2023', 'B'), 
(77777777, 7, 'Fall', '2023', 'B'),
(77777777, 13, 'Fall', '2023', 'A'),
(77777777, 14, 'Fall', '2023', 'A'),
(77777777, 15, 'Fall', '2023', 'A'); 
--BH transcript--
INSERT INTO transcript (stud_id, cid, csem, cyear, grade)
VALUES
(88888888, 2, 'Fall', '2023', null),
(88888888, 3, 'Fall', '2023', null);


INSERT INTO degrees VALUES (1, 12312312, 'BS/BA', 3.00, 'CS', 'GWU', '2023');
INSERT INTO recs VALUES (1, 12312312, 'JT', 'jt@gmail.com', 'professor', 'GWU', 'Great student');
INSERT INTO recs VALUES (2, 12312312, 'JT2', 'jt2@gmail.com', 'professor', 'GWU', 'Great student2');
INSERT INTO recs VALUES (3, 12312312, 'JT3', 'jt3@gmail.com', 'professor', 'GWU', 'Great student3');
INSERT INTO applications VALUES (1, 12312312, 'complete', 'T', 'MS', 1, NULL, 'FALL', 2023, 'CS TA for Python', 'I love snakes', 1, NULL, NULL, NULL, NULL);

INSERT INTO degrees VALUES (2, 666666666, 'BS/BA', 2.50, 'CS', 'GWU', '2023') ;
INSERT INTO recs VALUES (4, 666666666, 'BC', 'bc@gmail.com', 'professor', 'GWU', NULL);
INSERT INTO recs VALUES (5, 666666666, 'BC2', 'bc2@gmail.com', 'professor2', 'GWU', NULL);
INSERT INTO recs VALUES (6, 666666666, 'BC3', 'bc3@gmail.com', 'professor3', 'GWU', NULL);
INSERT INTO applications VALUES (2, 666666666, 'incomplete', 'F', 'MS', 2, NULL, 'Spring', 2024, 'I have all the experience', 'I have zero interests', NULL, NULL, NULL, NULL,NULL);

