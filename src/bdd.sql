CREATE DATABASE IF NOT EXISTS `constitucion`;
CREATE  TABLE IF NOT EXISTS `constitucion`.`codigos` (
  `id` INT NOT NULL AUTO_INCREMENT ,
  `codigo` VARCHAR(255) NOT NULL ,
  `segmento` TINYINT NOT NULL DEFAULT 0 ,
  `estado` TINYINT NOT NULL DEFAULT 0 ,
  `fecha_venta` TIMESTAMP ,
  PRIMARY KEY (`id`) )
ENGINE = InnoDB
DEFAULT CHARACTER SET = utf8
COLLATE = utf8_general_ci;