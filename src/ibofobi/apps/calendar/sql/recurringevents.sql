INSERT INTO "calendar_eventclasses" (SELECT NEXTVAL('calendar_eventclasses_id_seq'),'birthday');

INSERT INTO "calendar_recevents" (SELECT NEXTVAL('calendar_recevents_id_seq'),'Fødselsdag: adhh','2 sep *');
INSERT INTO "calendar_recevents_classes" (SELECT NEXTVAL('calendar_recevents_classes_id_seq'), CURRVAL('calendar_recevents_id_seq'), CURRVAL('calendar_eventclasses_id_seq'));
INSERT INTO "calendar_recevents" (SELECT NEXTVAL('calendar_recevents_id_seq'),'Fødselsdag: rabia','12 Oct *');
INSERT INTO "calendar_recevents" (SELECT NEXTVAL('calendar_recevents_id_seq'),'Fødselsdag: tanja','27 Oct *');
INSERT INTO "calendar_recevents" (SELECT NEXTVAL('calendar_recevents_id_seq'),'Fødselsdag: jette','30 Oct *');
INSERT INTO "calendar_recevents" (SELECT NEXTVAL('calendar_recevents_id_seq'),'Fødselsdag: amalie','17 Oct *');
INSERT INTO "calendar_recevents" (SELECT NEXTVAL('calendar_recevents_id_seq'),'Fødselsdag: fluff','9 sep *');
INSERT INTO "calendar_recevents" (SELECT NEXTVAL('calendar_recevents_id_seq'),'Bestyrelsesmøde','* * tuesday');
