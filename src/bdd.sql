CREATE DATABASE IF NOT EXISTS `constitucion`;
CREATE TABLE IF NOT EXISTS `constitucion`.`eventos` (
  `id` INT NOT NULL AUTO_INCREMENT,
  `nombre` TEXT NOT NULL,
  `fecha` DATETIME NOT NULL,
  PRIMARY KEY (`id`)
)
ENGINE = MyISAM;
CREATE TABLE IF NOT EXISTS `constitucion`.`codigos` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `codigo` VARCHAR(20) NOT NULL ,
  `segmento` TINYINT NOT NULL DEFAULT 0 ,
  `estado` TINYINT NOT NULL DEFAULT 0 ,
  `fecha_venta` TIMESTAMP ,
  `id_evento` INT DEFAULT 0,
  PRIMARY KEY (`id`)
)
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;
CREATE TABLE IF NOT EXISTS `constitucion`.`historial` (
	`id` INT PRIMARY KEY AUTO_INCREMENT,
	`codigo` VARCHAR(20) NOT NULL,
	`tipo` VARCHAR(20) NOT NULL DEFAULT 'Entrada',
	`fecha` TIMESTAMP
)
ENGINE = MyISAM;
/* add more columns if necessary */
CREATE TABLE IF NOT EXISTS `constitucion`.`socios` (
  `rut` CHAR(12) PRIMARY KEY,
  `nombre` VARCHAR(50) NOT NULL
)
ENGINE = MyISAM;

CREATE TABLE IF NOT EXISTS `constitucion`.`pulseras_socios` (
  `rut` CHAR(12) NOT NULL,
  `codigo` VARCHAR(20) NOT NULL,
  UNIQUE(`rut`, `codigo`)
)
ENGINE = MyISAM;

GRANT ALL ON `constitucion`.* TO 'testuser'@'localhost' IDENTIFIED BY 'handband';