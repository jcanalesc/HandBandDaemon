CREATE DATABASE IF NOT EXISTS `constitucion`;
CREATE  TABLE IF NOT EXISTS `constitucion`.`codigos` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `codigo` VARCHAR(255) NOT NULL ,
  `segmento` TINYINT NOT NULL DEFAULT 0 ,
  `estado` TINYINT NOT NULL DEFAULT 0 ,
  `fecha_venta` TIMESTAMP ,
  PRIMARY KEY (`id`) )
ENGINE = MyISAM
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;
CREATE TABLE IF NOT EXISTS `constitucion`.`historial` (
	`id` INT PRIMARY KEY AUTO_INCREMENT,
	`codigo` VARCHAR(255) NOT NULL,
	`tipo` VARCHAR(20) NOT NULL DEFAULT 'Entrada',
	`fecha` TIMESTAMP
)
ENGINE = MyISAM;
GRANT ALL ON `constitucion`.`codigos` TO 'testuser'@'localhost' IDENTIFIED BY 'handband';