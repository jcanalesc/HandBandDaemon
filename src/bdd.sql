DROP DATABASE IF EXISTS handband;
DROP USER 'testuser'@'localhost'
CREATE DATABASE handband;
GRANT ALL ON handband.* TO 'testuser'@'localhost' IDENTIFIED BY 'handband';
USE handband;
CREATE TABLE pulseras (
	id INTEGER PRIMARY KEY AUTO_INCREMENT,
	codigo varchar(60),
	impreso boolean default false,
	vendido boolean default true
);
