-- MySQL dump 10.13  Distrib 5.7.33, for Linux (x86_64)
--
-- Host: localhost    Database: seqdata
-- ------------------------------------------------------
-- Server version	5.7.33

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!40101 SET NAMES utf8 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

CREATE DATABASE seqdata;
use seqdata;

--
-- Table structure for table `alignmentparameters`
--

DROP TABLE IF EXISTS `alignmentparameters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `alignmentparameters` (
  `alignment` int(10) NOT NULL,
  `name` varchar(500) NOT NULL,
  `value` varchar(2000) NOT NULL,
  KEY `alignment` (`alignment`),
  CONSTRAINT `alignmentparameters_ibfk_1` FOREIGN KEY (`alignment`) REFERENCES `seqalignment` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `analysisinputs`
--

DROP TABLE IF EXISTS `analysisinputs`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `analysisinputs` (
  `analysis` int(10) NOT NULL,
  `alignment` int(10) NOT NULL,
  `inputtype` varchar(20) NOT NULL,
  KEY `fk_ai_analysis` (`analysis`),
  KEY `alignment` (`alignment`),
  CONSTRAINT `analysisinputs_ibfk_1` FOREIGN KEY (`analysis`) REFERENCES `seqdataanalysis` (`id`),
  CONSTRAINT `analysisinputs_ibfk_2` FOREIGN KEY (`alignment`) REFERENCES `seqalignment` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `analysisparameters`
--

DROP TABLE IF EXISTS `analysisparameters`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `analysisparameters` (
  `analysis` int(10) NOT NULL,
  `name` varchar(100) DEFAULT NULL,
  `value` varchar(1000) DEFAULT NULL,
  KEY `analysis` (`analysis`),
  CONSTRAINT `analysisparameters_ibfk_1` FOREIGN KEY (`analysis`) REFERENCES `seqdataanalysis` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `analysisresults`
--

DROP TABLE IF EXISTS `analysisresults`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `analysisresults` (
  `analysis` int(10) NOT NULL,
  `chromosome` int(10) NOT NULL,
  `startpos` int(10) NOT NULL DEFAULT '0',
  `stoppos` int(10) NOT NULL DEFAULT '0',
  `position` int(10) NOT NULL DEFAULT '0',
  `fgcount` double DEFAULT NULL,
  `bgcount` double DEFAULT NULL,
  `strength` double DEFAULT NULL,
  `peakshape` double DEFAULT NULL,
  `pvalue` double DEFAULT NULL,
  `fold_enrichment` double DEFAULT NULL,
  PRIMARY KEY (`analysis`,`chromosome`,`position`,`startpos`,`stoppos`),
  CONSTRAINT `analysisresults_ibfk_1` FOREIGN KEY (`analysis`) REFERENCES `seqdataanalysis` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `analysistype`
--

DROP TABLE IF EXISTS `analysistype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `analysistype` (
  `id` int(10) NOT NULL,
  `name` varchar(200) NOT NULL,
  PRIMARY KEY (`name`),
  UNIQUE KEY `id` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `seqalignment`
--

DROP TABLE IF EXISTS `seqalignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seqalignment` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `expt` int(10) NOT NULL,
  `name` varchar(200) NOT NULL,
  `genome` int(10) NOT NULL,
  `permissions` varchar(500) NOT NULL,
  `aligntype` int(10) NOT NULL,
  `numhits` int(15) DEFAULT NULL,
  `totalweight` float(17,2) DEFAULT NULL,
  `numtype2hits` int(15) DEFAULT NULL,
  `totaltype2weight` float(17,2) DEFAULT NULL,
  `numpairs` int(15) DEFAULT NULL,
  `totalpairweight` float(17,2) DEFAULT NULL,
  `aligndir` varchar(400) DEFAULT NULL,
  `alignfile` varchar(500) DEFAULT NULL,
  `idxfile` varchar(400) DEFAULT NULL,
  `collabalignid` varchar(200) DEFAULT NULL,
  `wiguploadstatus` enum('NOT UPLOADED','IN PROGRESS','FAILED','UPLOADED') DEFAULT 'NOT UPLOADED',
  `wiguploaddate` datetime DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `id` (`id`),
  KEY `fk_seqalignment_expt` (`expt`),
  KEY `name` (`name`),
  KEY `i_seqalignment_genome` (`genome`),
  CONSTRAINT `seqalignment_ibfk_1` FOREIGN KEY (`expt`) REFERENCES `seqexpt` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=29497 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `seqdataanalysis`
--

DROP TABLE IF EXISTS `seqdataanalysis`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seqdataanalysis` (
  `id` int(10) NOT NULL,
  `type` int(10) NOT NULL,
  `name` varchar(200) NOT NULL,
  `version` varchar(200) NOT NULL,
  `program` varchar(200) DEFAULT NULL,
  `active` int(1) DEFAULT '1',
  PRIMARY KEY (`name`,`version`),
  UNIQUE KEY `id` (`id`),
  KEY `fk_sa_type` (`type`),
  CONSTRAINT `seqdataanalysis_ibfk_1` FOREIGN KEY (`type`) REFERENCES `analysistype` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `seqexpt`
--

DROP TABLE IF EXISTS `seqexpt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seqexpt` (
  `id` int(10) NOT NULL AUTO_INCREMENT,
  `name` varchar(200) NOT NULL,
  `replicate` varchar(200) NOT NULL,
  `species` int(10) NOT NULL,
  `expttype` int(10) NOT NULL,
  `lab` int(10) NOT NULL,
  `exptcondition` int(10) NOT NULL,
  `expttarget` int(10) NOT NULL,
  `cellline` int(10) NOT NULL,
  `readtype` int(10) NOT NULL,
  `readlength` int(5) NOT NULL,
  `numreads` int(12) DEFAULT NULL,
  `collabid` varchar(200) DEFAULT NULL,
  `publicsource` varchar(200) DEFAULT NULL,
  `publicdbid` varchar(200) DEFAULT NULL,
  `fqfile` varchar(500) DEFAULT NULL,
  `exptnote` longtext,
  PRIMARY KEY (`name`,`replicate`),
  UNIQUE KEY `id` (`id`),
  KEY `name` (`name`,`replicate`),
  KEY `i_seqexpt_expttype` (`expttype`),
  KEY `i_seqexpt_lab` (`lab`),
  KEY `i_seqexpt_exptcondition` (`exptcondition`),
  KEY `i_seqexpt_expttarget` (`expttarget`),
  KEY `i_seqexpt_cellline` (`cellline`)
) ENGINE=InnoDB AUTO_INCREMENT=14317 DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Table structure for table `seqfiles`
--

DROP TABLE IF EXISTS `seqfiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!40101 SET character_set_client = utf8 */;
CREATE TABLE `seqfiles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `seqalignment` int(11) DEFAULT NULL,
  `name` char(50) DEFAULT NULL,
  `filetype` int(11) DEFAULT NULL,
  `tilesetUID` char(40) DEFAULT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `tilesetUID` (`tilesetUID`)
) ENGINE=InnoDB DEFAULT CHARSET=latin1;
/*!40101 SET character_set_client = @saved_cs_client */;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2021-02-04 11:03:49
