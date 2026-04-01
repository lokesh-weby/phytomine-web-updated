from django.db import models

# Create your models here.

class registration(models.Model):
    name=models.CharField(max_length=50,null=True)
    email=models.EmailField(max_length=50,null=True)
    mobile_no=models.CharField(max_length=50,null=True)
    department=models.CharField(max_length=50,null=True)


    rh_id= models.CharField(max_length=100, null=True)
    password=models.CharField(max_length=50,null=True)

    
    accept=models.BooleanField(default=False,null=True)
    reject=models.BooleanField(default=False,null=True)

    login=models.BooleanField(default=False, null=True)
    logout=models.BooleanField(default=False, null=True)


class phytomine(models.Model):
    user = models.ForeignKey(registration, on_delete=models.CASCADE, related_name='uploads', null=True)

    project_id= models.CharField(max_length=100, null=True)
    location=models.CharField(max_length=100,null=True)
    status=models.CharField(max_length=50,null=True,default="Pending")

    #for analyze
    cul_scan=models.BooleanField(default=False,null=True)
    acc_scan=models.BooleanField(default=False,null=True)
    ext_scan=models.BooleanField(default=False,null=True)
    sus_scan=models.BooleanField(default=False,null=True)


    #Values
    initial_fern_biomass=models.FloatField(null=True)
    final_fern_biomass=models.FloatField(null=True)
    growth_duration=models.FloatField(null=True)
    soil_ree_conc=models.FloatField(null=True)
    plant_ree_conc=models.FloatField(null=True)
    harvested_biomass=models.FloatField(null=True)
    extraction_eff=models.FloatField(null=True)
    initial_soil_ree=models.FloatField(null=True)
    final_soil_ree=models.FloatField(null=True)

    #CULTIVATOR Values
    biomass_increase=models.FloatField(null=True)
    growth_rate=models.FloatField(null=True)
    growth_eff=models.FloatField(null=True)

    #ACCUMULATOR Values
    total_metal=models.FloatField(null=True)
    uptake=models.FloatField(null=True)
    baf=models.FloatField(null=True)

    #EXTRACTOR Values
    recovered_metal=models.FloatField(null=True)
    loss=models.FloatField(null=True)
    recovery=models.FloatField(null=True)

    #SUSTAINER Values
    reduction=models.FloatField(null=True)
    safety_index=models.FloatField(null=True)
    env_status=models.CharField(max_length=50, null=True)



    #Encrypted Values
    e_initial_fern_biomass=models.TextField(null=True)
    e_final_fern_biomass=models.TextField(null=True)
    e_growth_duration=models.TextField(null=True)
    e_soil_ree_conc=models.TextField(null=True)
    e_plant_ree_conc=models.TextField(null=True)
    e_harvested_biomass=models.TextField(null=True)
    e_extraction_eff=models.TextField(null=True)
    e_initial_soil_ree=models.TextField(null=True)
    e_final_soil_ree=models.TextField(null=True)


    e_biomass_increase=models.TextField(null=True)
    e_growth_rate=models.TextField(null=True)
    e_growth_eff=models.TextField(null=True)


    e_total_metal=models.TextField(null=True)
    e_uptake=models.TextField(null=True)
    e_baf=models.TextField(null=True)

    e_recovered_metal=models.TextField(null=True)    
    e_loss=models.TextField(null=True)    
    e_recovery=models.TextField(null=True)    


    #CULTIVATOR Decrption Control
    cul_decrypt_key = models.TextField(null=True, blank=True)
    cul_get_key = models.BooleanField(default=False, null=True)
    cul_decrypt = models.BooleanField(default=False, null=True)

    #ACCUMULATOR Decrption Control
    acc_decrypt_key = models.TextField(null=True, blank=True)
    acc_get_key = models.BooleanField(default=False, null=True)
    acc_decrypt = models.BooleanField(default=False, null=True)

    #EXTRACTOR Decrption Control
    ext_decrypt_key = models.TextField(null=True, blank=True)
    ext_get_key = models.BooleanField(default=False, null=True)
    ext_decrypt = models.BooleanField(default=False, null=True)

    #SUSTAINER Decrption Control
    sus_decrypt_key = models.TextField(null=True, blank=True)
    sus_get_key = models.BooleanField(default=False, null=True)
    sus_decrypt = models.BooleanField(default=False, null=True)
    sus_signed_by = models.CharField(max_length=100, null=True, blank=True)

    #Signed By Fields for all modules
    cul_signed_by = models.CharField(max_length=100, null=True, blank=True)
    acc_signed_by = models.CharField(max_length=100, null=True, blank=True)
    ext_signed_by = models.CharField(max_length=100, null=True, blank=True)

    #Report
    admins_f_report=models.FileField(upload_to="Report/",null=True,blank=True)


    #Admins Report View
    admins_f_rep_view=models.BooleanField(default=False, null=True)