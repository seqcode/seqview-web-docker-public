-- MySQL dump 10.13  Distrib 8.0.17, for macos10.14 (x86_64)
--
-- Host: localhost    Database: browserwebsite
-- ------------------------------------------------------
-- Server version	8.0.17

/*!40101 SET @OLD_CHARACTER_SET_CLIENT=@@CHARACTER_SET_CLIENT */;
/*!40101 SET @OLD_CHARACTER_SET_RESULTS=@@CHARACTER_SET_RESULTS */;
/*!40101 SET @OLD_COLLATION_CONNECTION=@@COLLATION_CONNECTION */;
/*!50503 SET NAMES utf8mb4 */;
/*!40103 SET @OLD_TIME_ZONE=@@TIME_ZONE */;
/*!40103 SET TIME_ZONE='+00:00' */;
/*!40014 SET @OLD_UNIQUE_CHECKS=@@UNIQUE_CHECKS, UNIQUE_CHECKS=0 */;
/*!40014 SET @OLD_FOREIGN_KEY_CHECKS=@@FOREIGN_KEY_CHECKS, FOREIGN_KEY_CHECKS=0 */;
/*!40101 SET @OLD_SQL_MODE=@@SQL_MODE, SQL_MODE='NO_AUTO_VALUE_ON_ZERO' */;
/*!40111 SET @OLD_SQL_NOTES=@@SQL_NOTES, SQL_NOTES=0 */;

--
-- Table structure for table `auth_group`
--

DROP TABLE IF EXISTS `auth_group`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(150) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `name` (`name`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group`
--

LOCK TABLES `auth_group` WRITE;
/*!40000 ALTER TABLE `auth_group` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_group_permissions`
--

DROP TABLE IF EXISTS `auth_group_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_group_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `group_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_group_permissions_group_id_permission_id_0cd325b0_uniq` (`group_id`,`permission_id`),
  KEY `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_group_permissio_permission_id_84c5c92e_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_group_permissions_group_id_b120cbf9_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_group_permissions`
--

LOCK TABLES `auth_group_permissions` WRITE;
/*!40000 ALTER TABLE `auth_group_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_group_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_permission`
--

DROP TABLE IF EXISTS `auth_permission`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_permission` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `name` varchar(255) NOT NULL,
  `content_type_id` int(11) NOT NULL,
  `codename` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_permission_content_type_id_codename_01ab375a_uniq` (`content_type_id`,`codename`),
  CONSTRAINT `auth_permission_content_type_id_2f476e4b_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=81 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_permission`
--

LOCK TABLES `auth_permission` WRITE;
/*!40000 ALTER TABLE `auth_permission` DISABLE KEYS */;
INSERT INTO `auth_permission` VALUES (1,'Can add question',1,'add_question'),(2,'Can change question',1,'change_question'),(3,'Can delete question',1,'delete_question'),(4,'Can view question',1,'view_question'),(5,'Can add choice',2,'add_choice'),(6,'Can change choice',2,'change_choice'),(7,'Can delete choice',2,'delete_choice'),(8,'Can view choice',2,'view_choice'),(9,'Can add log entry',3,'add_logentry'),(10,'Can change log entry',3,'change_logentry'),(11,'Can delete log entry',3,'delete_logentry'),(12,'Can view log entry',3,'view_logentry'),(13,'Can add permission',4,'add_permission'),(14,'Can change permission',4,'change_permission'),(15,'Can delete permission',4,'delete_permission'),(16,'Can view permission',4,'view_permission'),(17,'Can add group',5,'add_group'),(18,'Can change group',5,'change_group'),(19,'Can delete group',5,'delete_group'),(20,'Can view group',5,'view_group'),(21,'Can add user',6,'add_user'),(22,'Can change user',6,'change_user'),(23,'Can delete user',6,'delete_user'),(24,'Can view user',6,'view_user'),(25,'Can add content type',7,'add_contenttype'),(26,'Can change content type',7,'change_contenttype'),(27,'Can delete content type',7,'delete_contenttype'),(28,'Can view content type',7,'view_contenttype'),(29,'Can add session',8,'add_session'),(30,'Can change session',8,'change_session'),(31,'Can delete session',8,'delete_session'),(32,'Can view session',8,'view_session'),(33,'Can add aligntype',9,'add_aligntype'),(34,'Can change aligntype',9,'change_aligntype'),(35,'Can delete aligntype',9,'delete_aligntype'),(36,'Can view aligntype',9,'view_aligntype'),(37,'Can add cellline',10,'add_cellline'),(38,'Can change cellline',10,'change_cellline'),(39,'Can delete cellline',10,'delete_cellline'),(40,'Can view cellline',10,'view_cellline'),(41,'Can add exptcondition',11,'add_exptcondition'),(42,'Can change exptcondition',11,'change_exptcondition'),(43,'Can delete exptcondition',11,'delete_exptcondition'),(44,'Can view exptcondition',11,'view_exptcondition'),(45,'Can add expttarget',12,'add_expttarget'),(46,'Can change expttarget',12,'change_expttarget'),(47,'Can delete expttarget',12,'delete_expttarget'),(48,'Can view expttarget',12,'view_expttarget'),(49,'Can add expttype',13,'add_expttype'),(50,'Can change expttype',13,'change_expttype'),(51,'Can delete expttype',13,'delete_expttype'),(52,'Can view expttype',13,'view_expttype'),(53,'Can add lab',14,'add_lab'),(54,'Can change lab',14,'change_lab'),(55,'Can delete lab',14,'delete_lab'),(56,'Can view lab',14,'view_lab'),(57,'Can add readtype',15,'add_readtype'),(58,'Can change readtype',15,'change_readtype'),(59,'Can delete readtype',15,'delete_readtype'),(60,'Can view readtype',15,'view_readtype'),(61,'Can add seqexpt',16,'add_seqexpt'),(62,'Can change seqexpt',16,'change_seqexpt'),(63,'Can delete seqexpt',16,'delete_seqexpt'),(64,'Can view seqexpt',16,'view_seqexpt'),(65,'Can add seqalignment',17,'add_seqalignment'),(66,'Can change seqalignment',17,'change_seqalignment'),(67,'Can delete seqalignment',17,'delete_seqalignment'),(68,'Can view seqalignment',17,'view_seqalignment'),(69,'Can add species',18,'add_species'),(70,'Can change species',18,'change_species'),(71,'Can delete species',18,'delete_species'),(72,'Can view species',18,'view_species'),(73,'Can add genome',19,'add_genome'),(74,'Can change genome',19,'change_genome'),(75,'Can delete genome',19,'delete_genome'),(76,'Can view genome',19,'view_genome'),(77,'Can add hi glass files',20,'add_higlassfiles'),(78,'Can change hi glass files',20,'change_higlassfiles'),(79,'Can delete hi glass files',20,'delete_higlassfiles'),(80,'Can view hi glass files',20,'view_higlassfiles');
/*!40000 ALTER TABLE `auth_permission` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user`
--

DROP TABLE IF EXISTS `auth_user`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `password` varchar(128) NOT NULL,
  `last_login` datetime(6) DEFAULT NULL,
  `is_superuser` tinyint(1) NOT NULL,
  `username` varchar(150) NOT NULL,
  `first_name` varchar(30) NOT NULL,
  `last_name` varchar(150) NOT NULL,
  `email` varchar(254) NOT NULL,
  `is_staff` tinyint(1) NOT NULL,
  `is_active` tinyint(1) NOT NULL,
  `date_joined` datetime(6) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `username` (`username`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user`
--

LOCK TABLES `auth_user` WRITE;
/*!40000 ALTER TABLE `auth_user` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_groups`
--

DROP TABLE IF EXISTS `auth_user_groups`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_groups` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `group_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_groups_user_id_group_id_94350c0c_uniq` (`user_id`,`group_id`),
  KEY `auth_user_groups_group_id_97559544_fk_auth_group_id` (`group_id`),
  CONSTRAINT `auth_user_groups_group_id_97559544_fk_auth_group_id` FOREIGN KEY (`group_id`) REFERENCES `auth_group` (`id`),
  CONSTRAINT `auth_user_groups_user_id_6a12ed8b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_groups`
--

LOCK TABLES `auth_user_groups` WRITE;
/*!40000 ALTER TABLE `auth_user_groups` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_groups` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `auth_user_user_permissions`
--

DROP TABLE IF EXISTS `auth_user_user_permissions`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `auth_user_user_permissions` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `user_id` int(11) NOT NULL,
  `permission_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `auth_user_user_permissions_user_id_permission_id_14a6b632_uniq` (`user_id`,`permission_id`),
  KEY `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` (`permission_id`),
  CONSTRAINT `auth_user_user_permi_permission_id_1fbb5f2c_fk_auth_perm` FOREIGN KEY (`permission_id`) REFERENCES `auth_permission` (`id`),
  CONSTRAINT `auth_user_user_permissions_user_id_a95ead1b_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `auth_user_user_permissions`
--

LOCK TABLES `auth_user_user_permissions` WRITE;
/*!40000 ALTER TABLE `auth_user_user_permissions` DISABLE KEYS */;
/*!40000 ALTER TABLE `auth_user_user_permissions` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `browserwebsite`
--

DROP TABLE IF EXISTS `browserwebsite`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `browserwebsite` (
  `id` int(11) DEFAULT NULL,
  `name` varchar(100) DEFAULT NULL
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `browserwebsite`
--

LOCK TABLES `browserwebsite` WRITE;
/*!40000 ALTER TABLE `browserwebsite` DISABLE KEYS */;
/*!40000 ALTER TABLE `browserwebsite` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_admin_log`
--

DROP TABLE IF EXISTS `django_admin_log`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_admin_log` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `action_time` datetime(6) NOT NULL,
  `object_id` longtext,
  `object_repr` varchar(200) NOT NULL,
  `action_flag` smallint(5) unsigned NOT NULL,
  `change_message` longtext NOT NULL,
  `content_type_id` int(11) DEFAULT NULL,
  `user_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `django_admin_log_content_type_id_c4bce8eb_fk_django_co` (`content_type_id`),
  KEY `django_admin_log_user_id_c564eba6_fk_auth_user_id` (`user_id`),
  CONSTRAINT `django_admin_log_content_type_id_c4bce8eb_fk_django_co` FOREIGN KEY (`content_type_id`) REFERENCES `django_content_type` (`id`),
  CONSTRAINT `django_admin_log_user_id_c564eba6_fk_auth_user_id` FOREIGN KEY (`user_id`) REFERENCES `auth_user` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_admin_log`
--

LOCK TABLES `django_admin_log` WRITE;
/*!40000 ALTER TABLE `django_admin_log` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_admin_log` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_content_type`
--

DROP TABLE IF EXISTS `django_content_type`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_content_type` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app_label` varchar(100) NOT NULL,
  `model` varchar(100) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `django_content_type_app_label_model_76bd3d3b_uniq` (`app_label`,`model`)
) ENGINE=InnoDB AUTO_INCREMENT=21 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_content_type`
--

LOCK TABLES `django_content_type` WRITE;
/*!40000 ALTER TABLE `django_content_type` DISABLE KEYS */;
INSERT INTO `django_content_type` VALUES (3,'admin','logentry'),(5,'auth','group'),(4,'auth','permission'),(6,'auth','user'),(7,'contenttypes','contenttype'),(9,'genomeTrackSidebar','aligntype'),(10,'genomeTrackSidebar','cellline'),(2,'genomeTrackSidebar','choice'),(11,'genomeTrackSidebar','exptcondition'),(12,'genomeTrackSidebar','expttarget'),(13,'genomeTrackSidebar','expttype'),(19,'genomeTrackSidebar','genome'),(20,'genomeTrackSidebar','higlassfiles'),(14,'genomeTrackSidebar','lab'),(1,'genomeTrackSidebar','question'),(15,'genomeTrackSidebar','readtype'),(17,'genomeTrackSidebar','seqalignment'),(16,'genomeTrackSidebar','seqexpt'),(18,'genomeTrackSidebar','species'),(8,'sessions','session');
/*!40000 ALTER TABLE `django_content_type` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_migrations`
--

DROP TABLE IF EXISTS `django_migrations`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_migrations` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `app` varchar(255) NOT NULL,
  `name` varchar(255) NOT NULL,
  `applied` datetime(6) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=23 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_migrations`
--

LOCK TABLES `django_migrations` WRITE;
/*!40000 ALTER TABLE `django_migrations` DISABLE KEYS */;
INSERT INTO `django_migrations` VALUES (1,'contenttypes','0001_initial','2019-09-06 18:50:25.630303'),(2,'auth','0001_initial','2019-09-06 18:50:25.681182'),(3,'admin','0001_initial','2019-09-06 18:50:25.882151'),(4,'admin','0002_logentry_remove_auto_add','2019-09-06 18:50:25.913786'),(5,'admin','0003_logentry_add_action_flag_choices','2019-09-06 18:50:25.919363'),(6,'contenttypes','0002_remove_content_type_name','2019-09-06 18:50:25.950885'),(7,'auth','0002_alter_permission_name_max_length','2019-09-06 18:50:25.967162'),(8,'auth','0003_alter_user_email_max_length','2019-09-06 18:50:25.981091'),(9,'auth','0004_alter_user_username_opts','2019-09-06 18:50:25.987055'),(10,'auth','0005_alter_user_last_login_null','2019-09-06 18:50:26.006063'),(11,'auth','0006_require_contenttypes_0002','2019-09-06 18:50:26.007454'),(12,'auth','0007_alter_validators_add_error_messages','2019-09-06 18:50:26.012960'),(13,'auth','0008_alter_user_username_max_length','2019-09-06 18:50:26.033112'),(14,'auth','0009_alter_user_last_name_max_length','2019-09-06 18:50:26.053498'),(15,'auth','0010_alter_group_name_max_length','2019-09-06 18:50:26.064046'),(16,'auth','0011_update_proxy_permissions','2019-09-06 18:50:26.069906'),(17,'genomeTrackSidebar','0001_initial','2019-09-06 18:50:26.084843'),(18,'sessions','0001_initial','2019-09-06 18:50:26.102993'),(19,'genomeTrackSidebar','0002_aligntype_cellline_exptcondition_expttarget_expttype_lab_readtype_seqalignment_seqexpt','2019-09-06 19:17:20.669280'),(20,'genomeTrackSidebar','0003_auto_20190906_1926','2019-09-06 19:27:05.977580'),(21,'genomeTrackSidebar','0004_auto_20190916_2059','2019-09-17 13:38:47.079096'),(22,'genomeTrackSidebar','0005_auto_20190917_1436','2019-09-17 14:36:42.128327');
/*!40000 ALTER TABLE `django_migrations` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `django_session`
--

DROP TABLE IF EXISTS `django_session`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `django_session` (
  `session_key` varchar(40) NOT NULL,
  `session_data` longtext NOT NULL,
  `expire_date` datetime(6) NOT NULL,
  PRIMARY KEY (`session_key`),
  KEY `django_session_expire_date_a5c62663` (`expire_date`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `django_session`
--

LOCK TABLES `django_session` WRITE;
/*!40000 ALTER TABLE `django_session` DISABLE KEYS */;
/*!40000 ALTER TABLE `django_session` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genomeTrackSidebar_aligntype`
--

DROP TABLE IF EXISTS `genomeTrackSidebar_aligntype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genomeTrackSidebar_aligntype` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genomeTrackSidebar_aligntype`
--

LOCK TABLES `genomeTrackSidebar_aligntype` WRITE;
/*!40000 ALTER TABLE `genomeTrackSidebar_aligntype` DISABLE KEYS */;
INSERT INTO `genomeTrackSidebar_aligntype` VALUES (1,'single');
/*!40000 ALTER TABLE `genomeTrackSidebar_aligntype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genomeTrackSidebar_cellline`
--

DROP TABLE IF EXISTS `genomeTrackSidebar_cellline`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genomeTrackSidebar_cellline` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genomeTrackSidebar_cellline`
--

LOCK TABLES `genomeTrackSidebar_cellline` WRITE;
/*!40000 ALTER TABLE `genomeTrackSidebar_cellline` DISABLE KEYS */;
INSERT INTO `genomeTrackSidebar_cellline` VALUES (1,'CRL-2977');
/*!40000 ALTER TABLE `genomeTrackSidebar_cellline` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genomeTrackSidebar_exptcondition`
--

DROP TABLE IF EXISTS `genomeTrackSidebar_exptcondition`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genomeTrackSidebar_exptcondition` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genomeTrackSidebar_exptcondition`
--

LOCK TABLES `genomeTrackSidebar_exptcondition` WRITE;
/*!40000 ALTER TABLE `genomeTrackSidebar_exptcondition` DISABLE KEYS */;
INSERT INTO `genomeTrackSidebar_exptcondition` VALUES (1,'ES');
/*!40000 ALTER TABLE `genomeTrackSidebar_exptcondition` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genomeTrackSidebar_expttarget`
--

DROP TABLE IF EXISTS `genomeTrackSidebar_expttarget`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genomeTrackSidebar_expttarget` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genomeTrackSidebar_expttarget`
--

LOCK TABLES `genomeTrackSidebar_expttarget` WRITE;
/*!40000 ALTER TABLE `genomeTrackSidebar_expttarget` DISABLE KEYS */;
INSERT INTO `genomeTrackSidebar_expttarget` VALUES (1,'Cdx2');
/*!40000 ALTER TABLE `genomeTrackSidebar_expttarget` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genomeTrackSidebar_expttype`
--

DROP TABLE IF EXISTS `genomeTrackSidebar_expttype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genomeTrackSidebar_expttype` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genomeTrackSidebar_expttype`
--

LOCK TABLES `genomeTrackSidebar_expttype` WRITE;
/*!40000 ALTER TABLE `genomeTrackSidebar_expttype` DISABLE KEYS */;
INSERT INTO `genomeTrackSidebar_expttype` VALUES (1,'CHIPSEQ');
/*!40000 ALTER TABLE `genomeTrackSidebar_expttype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genomeTrackSidebar_genome`
--

DROP TABLE IF EXISTS `genomeTrackSidebar_genome`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genomeTrackSidebar_genome` (
  `id` int(11) NOT NULL,
  `version` varchar(200) NOT NULL,
  `species_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `genomeTrackSidebar_g_species_id_db72d4c8_fk_genomeTra` (`species_id`),
  CONSTRAINT `genomeTrackSidebar_g_species_id_db72d4c8_fk_genomeTra` FOREIGN KEY (`species_id`) REFERENCES `genometracksidebar_species` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genomeTrackSidebar_genome`
--

LOCK TABLES `genomeTrackSidebar_genome` WRITE;
/*!40000 ALTER TABLE `genomeTrackSidebar_genome` DISABLE KEYS */;
INSERT INTO `genomeTrackSidebar_genome` VALUES (1,'mm9',1),(2,'mm10',1);
/*!40000 ALTER TABLE `genomeTrackSidebar_genome` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genomeTrackSidebar_higlassfiles`
--

DROP TABLE IF EXISTS `genomeTrackSidebar_higlassfiles`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genomeTrackSidebar_higlassfiles` (
  `id` int(11) NOT NULL AUTO_INCREMENT,
  `tilesetUID` varchar(40) NOT NULL,
  `seqalignment_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  UNIQUE KEY `genomeTrackSidebar_higlassfiles_seqalignment_id_ced4c665_uniq` (`seqalignment_id`),
  CONSTRAINT `genomeTrackSidebar_h_seqalignment_id_ced4c665_fk_genomeTra` FOREIGN KEY (`seqalignment_id`) REFERENCES `genometracksidebar_seqalignment` (`id`)
) ENGINE=InnoDB AUTO_INCREMENT=3 DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genomeTrackSidebar_higlassfiles`
--

LOCK TABLES `genomeTrackSidebar_higlassfiles` WRITE;
/*!40000 ALTER TABLE `genomeTrackSidebar_higlassfiles` DISABLE KEYS */;
INSERT INTO `genomeTrackSidebar_higlassfiles` VALUES (1,'M-LTWpoGQ0iQvfJBtzXg4A',1),(2,'Ch2IpAcXR12cp4aRFfDJyw',2);
/*!40000 ALTER TABLE `genomeTrackSidebar_higlassfiles` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genomeTrackSidebar_lab`
--

DROP TABLE IF EXISTS `genomeTrackSidebar_lab`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genomeTrackSidebar_lab` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genomeTrackSidebar_lab`
--

LOCK TABLES `genomeTrackSidebar_lab` WRITE;
/*!40000 ALTER TABLE `genomeTrackSidebar_lab` DISABLE KEYS */;
INSERT INTO `genomeTrackSidebar_lab` VALUES (1,'Mazzoni');
/*!40000 ALTER TABLE `genomeTrackSidebar_lab` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genomeTrackSidebar_readtype`
--

DROP TABLE IF EXISTS `genomeTrackSidebar_readtype`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genomeTrackSidebar_readtype` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genomeTrackSidebar_readtype`
--

LOCK TABLES `genomeTrackSidebar_readtype` WRITE;
/*!40000 ALTER TABLE `genomeTrackSidebar_readtype` DISABLE KEYS */;
INSERT INTO `genomeTrackSidebar_readtype` VALUES (1,'single');
/*!40000 ALTER TABLE `genomeTrackSidebar_readtype` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genomeTrackSidebar_seqalignment`
--

DROP TABLE IF EXISTS `genomeTrackSidebar_seqalignment`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genomeTrackSidebar_seqalignment` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `genome_id` int(11) NOT NULL,
  `permissions` varchar(200) NOT NULL,
  `aligntype_id` int(11) NOT NULL,
  `numhits` int(11) NOT NULL,
  `totalweight` double NOT NULL,
  `aligndir` varchar(200) NOT NULL,
  `alignfile` varchar(200) NOT NULL,
  `idxfile` varchar(200) NOT NULL,
  `collabalignid` varchar(200) NOT NULL,
  `expt_id` int(11) NOT NULL,
  PRIMARY KEY (`id`),
  KEY `genomeTrackSidebar_s_expt_id_e78ac0a4_fk_genomeTra` (`expt_id`),
  KEY `genomeTrackSidebar_seqalignment_aligntype_id_e4699e80` (`aligntype_id`),
  KEY `genomeTrackSidebar_seqalignment_genome_id_705cc7ce` (`genome_id`),
  CONSTRAINT `genomeTrackSidebar_s_aligntype_id_e4699e80_fk_genomeTra` FOREIGN KEY (`aligntype_id`) REFERENCES `genometracksidebar_aligntype` (`id`),
  CONSTRAINT `genomeTrackSidebar_s_expt_id_e78ac0a4_fk_genomeTra` FOREIGN KEY (`expt_id`) REFERENCES `genometracksidebar_seqexpt` (`id`),
  CONSTRAINT `genomeTrackSidebar_s_genome_id_705cc7ce_fk_genomeTra` FOREIGN KEY (`genome_id`) REFERENCES `genometracksidebar_genome` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genomeTrackSidebar_seqalignment`
--

LOCK TABLES `genomeTrackSidebar_seqalignment` WRITE;
/*!40000 ALTER TABLE `genomeTrackSidebar_seqalignment` DISABLE KEYS */;
INSERT INTO `genomeTrackSidebar_seqalignment` VALUES (1,'Filtered',1,'all',1,10000,5,'/','21144','21144','',1),(2,'Second',1,'all',1,10000,5,'/','21144','21144','',1);
/*!40000 ALTER TABLE `genomeTrackSidebar_seqalignment` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genomeTrackSidebar_seqexpt`
--

DROP TABLE IF EXISTS `genomeTrackSidebar_seqexpt`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genomeTrackSidebar_seqexpt` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  `replicate` varchar(200) NOT NULL,
  `species_id` int(11) NOT NULL,
  `expttpe_id` int(11) NOT NULL,
  `lab_id` int(11) NOT NULL,
  `exptcondition_id` int(11) NOT NULL,
  `expttarget_id` int(11) NOT NULL,
  `cellline_id` int(11) NOT NULL,
  `readtype_id` int(11) NOT NULL,
  `readlength` int(11) NOT NULL,
  `numreads` int(11) NOT NULL,
  `collabid` varchar(200) NOT NULL,
  `publicsource` varchar(200) NOT NULL,
  `publicdbid` varchar(200) NOT NULL,
  `fqfile` varchar(200) NOT NULL,
  `exptnote` longtext NOT NULL,
  PRIMARY KEY (`id`),
  KEY `genomeTrackSidebar_seqexpt_cellline_id_88ac91ad` (`cellline_id`),
  KEY `genomeTrackSidebar_seqexpt_exptcondition_id_6a7299fb` (`exptcondition_id`),
  KEY `genomeTrackSidebar_seqexpt_expttarget_id_b7e96758` (`expttarget_id`),
  KEY `genomeTrackSidebar_seqexpt_expttpe_id_08887b8f` (`expttpe_id`),
  KEY `genomeTrackSidebar_seqexpt_lab_id_d99e8625` (`lab_id`),
  KEY `genomeTrackSidebar_seqexpt_readtype_id_cf149ba7` (`readtype_id`),
  KEY `genomeTrackSidebar_seqexpt_species_id_aa1cdfe4` (`species_id`),
  CONSTRAINT `genomeTrackSidebar_s_cellline_id_88ac91ad_fk_genomeTra` FOREIGN KEY (`cellline_id`) REFERENCES `genometracksidebar_cellline` (`id`),
  CONSTRAINT `genomeTrackSidebar_s_exptcondition_id_6a7299fb_fk_genomeTra` FOREIGN KEY (`exptcondition_id`) REFERENCES `genometracksidebar_exptcondition` (`id`),
  CONSTRAINT `genomeTrackSidebar_s_expttarget_id_b7e96758_fk_genomeTra` FOREIGN KEY (`expttarget_id`) REFERENCES `genometracksidebar_expttarget` (`id`),
  CONSTRAINT `genomeTrackSidebar_s_expttpe_id_08887b8f_fk_genomeTra` FOREIGN KEY (`expttpe_id`) REFERENCES `genometracksidebar_expttype` (`id`),
  CONSTRAINT `genomeTrackSidebar_s_lab_id_d99e8625_fk_genomeTra` FOREIGN KEY (`lab_id`) REFERENCES `genometracksidebar_lab` (`id`),
  CONSTRAINT `genomeTrackSidebar_s_readtype_id_cf149ba7_fk_genomeTra` FOREIGN KEY (`readtype_id`) REFERENCES `genometracksidebar_readtype` (`id`),
  CONSTRAINT `genomeTrackSidebar_s_species_id_aa1cdfe4_fk_genomeTra` FOREIGN KEY (`species_id`) REFERENCES `genometracksidebar_species` (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genomeTrackSidebar_seqexpt`
--

LOCK TABLES `genomeTrackSidebar_seqexpt` WRITE;
/*!40000 ALTER TABLE `genomeTrackSidebar_seqexpt` DISABLE KEYS */;
INSERT INTO `genomeTrackSidebar_seqexpt` VALUES (1,'21144_Cdx2_F1804_ESC_Rosa26pr-DoxRepr-Cdx2_Dox-LIF_NoDox-24h-DSG_XO','1',1,1,1,1,1,1,1,30,10000,'','','','','');
/*!40000 ALTER TABLE `genomeTrackSidebar_seqexpt` ENABLE KEYS */;
UNLOCK TABLES;

--
-- Table structure for table `genomeTrackSidebar_species`
--

DROP TABLE IF EXISTS `genomeTrackSidebar_species`;
/*!40101 SET @saved_cs_client     = @@character_set_client */;
/*!50503 SET character_set_client = utf8mb4 */;
CREATE TABLE `genomeTrackSidebar_species` (
  `id` int(11) NOT NULL,
  `name` varchar(200) NOT NULL,
  PRIMARY KEY (`id`)
) ENGINE=InnoDB DEFAULT CHARSET=utf8mb4 COLLATE=utf8mb4_0900_ai_ci;
/*!40101 SET character_set_client = @saved_cs_client */;

--
-- Dumping data for table `genomeTrackSidebar_species`
--

LOCK TABLES `genomeTrackSidebar_species` WRITE;
/*!40000 ALTER TABLE `genomeTrackSidebar_species` DISABLE KEYS */;
INSERT INTO `genomeTrackSidebar_species` VALUES (1,'mus musculus'),(2,'Homo Sapiens');
/*!40000 ALTER TABLE `genomeTrackSidebar_species` ENABLE KEYS */;
UNLOCK TABLES;
/*!40103 SET TIME_ZONE=@OLD_TIME_ZONE */;

/*!40101 SET SQL_MODE=@OLD_SQL_MODE */;
/*!40014 SET FOREIGN_KEY_CHECKS=@OLD_FOREIGN_KEY_CHECKS */;
/*!40014 SET UNIQUE_CHECKS=@OLD_UNIQUE_CHECKS */;
/*!40101 SET CHARACTER_SET_CLIENT=@OLD_CHARACTER_SET_CLIENT */;
/*!40101 SET CHARACTER_SET_RESULTS=@OLD_CHARACTER_SET_RESULTS */;
/*!40101 SET COLLATION_CONNECTION=@OLD_COLLATION_CONNECTION */;
/*!40111 SET SQL_NOTES=@OLD_SQL_NOTES */;

-- Dump completed on 2019-09-17 11:35:32
